import json
import mimetypes
import os
from wsgiref.util import FileWrapper

from django.db.models import Q
from django.http import Http404
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.views.generic import TemplateView
from django.utils.translation import gettext as _

from auth_main.models import User
from competition.utils import get_swim_params, is_correct_time, get_points
from competition.utils.ResultsExcel import ResultsExcel
from core.models import Competition, UserDistance
from core.utils import activate_language, get_session_attributes, querysetdistance_to_dict


class UserDistanceRegistrationView(TemplateView):
    template_name = 'competition/user_list.html'

    def get(self, request, *args, **kwargs):
        activate_language(request.session)
        opt = {}

        competition = get_object_or_404(Competition, pk=kwargs['pk'])
        if request.user.is_authenticated and request.user.profile.role == 2:
            if competition.created_by == request.user.id or request.user.is_admin:
                opt['users_distances'] = competition.getAllUsersDistances()
                opt['competition'] = competition
                return render(request, self.template_name, dict(opt, **get_session_attributes(request)))

        raise Http404

    def post(self, request, *args, **kwargs):
        competition = get_object_or_404(Competition, pk=kwargs['pk'])
        if request.user.is_authenticated and request.user.profile.role == 2:
            if competition.created_by == request.user.id or request.user.is_admin:
                UserDistance.objects.filter(distance__competition=competition, user__id=request.POST['user_id']).update(is_finished=True)
                request.session['alerts'] = [{'type': 'success', 'message': _('User has been finished registration!')}]
                return redirect('/competition/{}/list'.format(competition.id))

        raise Http404


class FindUserView(View):
    def post(self, request, *args, **kwargs):
        activate_language(request.session)
        data = json.loads(request.body.decode('utf-8'))
        search = data['search'].strip()
        competition = get_object_or_404(Competition, pk=kwargs['pk'])
        if ' ' in search:
            search = search.split(' ')
            query = Q()
            for x in search:
                query = query | (Q(user__first_name__contains=x) | Q(user__last_name__contains=x))
            users = UserDistance.objects.filter(distance__competition=competition).filter(query).\
                values('user').distinct()[:10]
        else:
            users = UserDistance.objects.filter(distance__competition=competition).filter(Q(user__first_name__contains=search) | Q(user__last_name__contains=search))\
                .values('user').distinct()[:10]
        users_json = json.dumps(querysetdistance_to_dict(users, competition))
        return HttpResponse(users_json)


class FinishUserRegistrationView(View):
    def get(self, request, *args, **kwargs):
        competition = get_object_or_404(Competition, pk=kwargs['pk'])
        if request.user.is_authenticated and request.user.profile.role == 2:
            if competition.created_by == request.user.id or request.user.is_admin:
                UserDistance.objects.filter(distance__competition=competition, user__id=kwargs['user_id']).update(
                    is_finished=True)
                user = get_object_or_404(User, id=kwargs['user_id'])
                request.session['alerts'] = [{'type': 'success', 'message': _('%(user)s has been finished registration!') % {'user': user.get_full_name()}}]
                return redirect('/competition/{}/list'.format(competition.id))

        raise Http404


class RemoveUserRegistrationView(View):
    def get(self, request, *args, **kwargs):
        competition = get_object_or_404(Competition, pk=kwargs['pk'])
        if request.user.is_authenticated and request.user.profile.role == 2:
            if competition.created_by == request.user.id or request.user.is_admin:
                UserDistance.objects.filter(distance__competition=competition, user__id=kwargs['user_id']).update(
                    is_finished=False, points=None, result_time='')
                user = get_object_or_404(User, id=kwargs['user_id'])
                request.session['alerts'] = [{'type': 'success',
                                              'message': _('%(user)s has been removed from registration!') % {
                                                  'user': user.get_full_name()}}]
                return redirect('/competition/{}/list'.format(competition.id))

        raise Http404


class FinishCompetitionRegistration(View):
    def get(self, request, *args, **kwargs):
        competition = get_object_or_404(Competition, pk=kwargs['pk'])
        if request.user.is_authenticated and request.user.profile.role == 2:
            if competition.created_by == request.user.id or request.user.is_admin and not competition.is_register_finished:
                competition.is_register_finished = True
                competition.save()
                request.session['alerts'] = [{'type': 'success',
                                              'message': _('Competition registration has been finished!')}]
                return redirect('/competition/{}/list'.format(competition.id))

        raise Http404


class ResumeCompetitionRegistration(View):
    def get(self, request, *args, **kwargs):
        competition = get_object_or_404(Competition, pk=kwargs['pk'])
        if request.user.is_authenticated and request.user.profile.role == 2:
            if competition.created_by == request.user.id or request.user.is_admin and competition.is_register_finished:
                competition.is_register_finished = False
                competition.save()
                request.session['alerts'] = [{'type': 'success',
                                              'message': _('Competition registration has been resumed!')}]
                return redirect('/competition/{}/list'.format(competition.id))

        raise Http404


class SwimResultsView(TemplateView):
    template_name = 'competition/swims_results.html'

    def get(self, request, *args, **kwargs):
        activate_language(request.session)
        opt = {}

        day = int(kwargs['day'])
        if day not in [1, 2]:
            raise Http404
        if request.user.is_authenticated and request.user.profile.role == 2:
            competition = get_object_or_404(Competition, id=kwargs['pk'])
            if competition.created_by == request.user.id or request.user.is_admin:
                users_distances, last_swim = get_swim_params(int(kwargs['swim']), competition, day)
                opt['users_distances'] = users_distances
                opt['swim_n'] = kwargs['swim']
                opt['day'] = _('Day {}'.format(day))
                opt['day_n'] = day
                opt['is_next_day'] = competition.count_days > day
                opt['is_prev_day'] = day > 1
                opt['is_next'] = last_swim > int(kwargs['swim'])
                opt['is_prev'] = int(kwargs['swim']) - 1 != 0
                opt['competition'] = competition
                return render(request, self.template_name, dict(opt, **get_session_attributes(request)))

        raise Http404

    def post(self, request, *args, **kwargs):
        activate_language(request.session)

        day = int(kwargs['day'])
        if day not in [1, 2]:
            raise Http404
        if request.user.is_authenticated and request.user.profile.role == 2:
            competition = get_object_or_404(Competition, id=kwargs['pk'])
            if competition.created_by == request.user.id or request.user.is_admin:
                for attr in request.POST:
                    if 'result' not in attr:
                        continue
                    user_distance_id = int(attr.split('_')[-1])
                    if is_correct_time(request.POST[attr]):
                        user_distance = UserDistance.objects.filter(id=user_distance_id).first()
                        user_distance.result_time = request.POST[attr]
                        user_distance.points = get_points(user_distance.distance, user_distance.user, request.POST[attr], day, competition)
                        print(user_distance.points)
                        user_distance.save()
                    else:
                        request.session['alerts'] = [{'type': 'error',
                                                      'message': _('%(user)s result time has wrong format. Please try again.') % {
                                                          'user': UserDistance.objects.filter(id=user_distance_id).first().user.full_name
                                                      }}]
                if 'alerts' not in request.session:
                    request.session['alerts'] = [{'type': 'success', 'message': _('Success!')}]

                return redirect('/competition/{}/swim/{}/day/{}'.format(competition.pk, kwargs['swim'], day))
        raise Http404


class DownloadResultsView(View):
    def get(self, request, *args, **kwargs):
        activate_language(request.session)

        if request.user.is_authenticated and request.user.profile.role == 2:
            competition = get_object_or_404(Competition, id=kwargs['pk'])
            if competition.created_by == request.user.id or request.user.is_admin:
                path = ResultsExcel(competition).create_excel()
                if path is None:
                    return
                file_wrapper = FileWrapper(open(path, 'rb'))
                file_mimetype = mimetypes.guess_type(path)
                response = HttpResponse(file_wrapper, content_type=file_mimetype)
                response['X-Sendfile'] = path
                response['Content-Length'] = os.stat(path).st_size
                response['Content-Disposition'] = 'attachment; filename={}'.format(
                    'results.xlsx')
                return response
            raise Http404
        return redirect('/auth/login')


class DownloadRatingView(View):
    def get(self, request, *args, **kwargs):
        activate_language(request.session)

        if request.user.is_authenticated and request.user.profile.role == 2:
            competition = get_object_or_404(Competition, id=kwargs['pk'])
            if competition.created_by == request.user.id or request.user.is_admin:
                path = ResultsExcel(competition).create_rating()
                if path is None:
                    return
                file_wrapper = FileWrapper(open(path, 'rb'))
                file_mimetype = mimetypes.guess_type(path)
                response = HttpResponse(file_wrapper, content_type=file_mimetype)
                response['X-Sendfile'] = path
                response['Content-Length'] = os.stat(path).st_size
                response['Content-Disposition'] = 'attachment; filename={}'.format(
                    'rating.xlsx')
                return response
            raise Http404
        return redirect('/auth/login')
