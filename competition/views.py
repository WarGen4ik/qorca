import json
import mimetypes
import os
from wsgiref.util import FileWrapper

from django.core.paginator import PageNotAnInteger, EmptyPage, Paginator
from django.db.models import Q
from django.http import Http404
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.views.generic import TemplateView
from django.utils.translation import gettext as _

from auth_main.models import User
from competition.utils import get_swim_params, is_correct_time, get_points, time_to_str, get_time_int
from competition.utils.ResultsExcel import ResultsExcel
from core.models import Competition, UserDistance, CompetitionUser, Distance
from core.utils import activate_language, get_session_attributes, querysetdistance_to_dict


class UserDistanceRegistrationView(TemplateView):
    template_name = 'competition/user_list.html'

    def get(self, request, *args, **kwargs):
        activate_language(request.session)
        opt = {}

        competition = get_object_or_404(Competition, pk=kwargs['pk'])
        if request.user.is_authenticated and request.user.profile.role == 2:
            if competition.created_by == request.user.id or request.user.is_admin:
                paginator = Paginator(competition.getAllUsersDistances(), 20)
                page = request.GET.get('page', 1)

                try:
                    users_distances = paginator.page(page)
                except PageNotAnInteger:
                    users_distances = paginator.page(1)
                except EmptyPage:
                    users_distances = paginator.page(paginator.num_pages)

                opt['users_distances'] = users_distances
                opt['competition'] = competition
                return render(request, self.template_name, dict(opt, **get_session_attributes(request)))

        raise Http404

    def post(self, request, *args, **kwargs):
        competition = get_object_or_404(Competition, pk=kwargs['pk'])
        if request.user.is_authenticated and request.user.profile.role == 2:
            if competition.created_by == request.user.id or request.user.is_admin:
                UserDistance.objects.filter(distance__competition=competition, user__id=request.POST['user_id']).update(is_finished=True)
                request.session['alerts'] = [{'type': 'success', 'message': _('User has finished registration!')}]
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
                request.session['alerts'] = [{'type': 'success', 'message': _('%(user)s has finished registration!') % {'user': user.get_full_name()}}]
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
                                              'message': _('%(user)s has removed from registration!') % {
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
                                              'message': _('Competition registration has finished!')}]
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
                                              'message': _('Competition registration has resumed!')}]
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
                opt['distance'] = users_distances[0].distance
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


class UserDistancesView(TemplateView):
    template_name = 'competition/user_distances.html'

    def get(self, request, *args, **kwargs):
        activate_language(request.session)
        if not request.user.is_authenticated:
            return redirect('/')
        competition = get_object_or_404(Competition, pk=kwargs['pk'])
        user = get_object_or_404(User, pk=kwargs['user_id'])

        distances = Distance.objects.filter(competition=competition).all()

        ret_1 = []
        ret_2 = []
        is_day_2 = False
        for distance in distances:
            if distance.day == 2:
                is_day_2 = True
                user_distance = UserDistance.objects.filter(user=user, distance=distance).first()
                temp = {'distance': distance}
                if user_distance:
                    temp['time'] = time_to_str(user_distance.pre_time)
                else: temp['time'] = ''
                ret_2.append(temp)
            else:
                user_distance = UserDistance.objects.filter(user=user, distance=distance).first()
                temp = {'distance': distance}
                if user_distance:
                    temp['time'] = time_to_str(user_distance.pre_time)
                else: temp['time'] = ''
                ret_1.append(temp)

        return render(request, self.template_name, {'types': Distance.TYPES,
                                                    'competition': competition,
                                                    'ret_1': ret_1,
                                                    'ret_2': ret_2,
                                                    'curr_user': user,
                                                    'is_day_2': is_day_2
                                                    })

    def post(self, request, *args, **kwargs):
        activate_language(request.session)
        if not request.user.is_authenticated:
            return redirect('/')
        competition = Competition.objects.get(pk=kwargs['pk'])
        user = get_object_or_404(User, pk=kwargs['user_id'])
        distances = Distance.objects.filter(competition=competition)
        data = request.POST

        for distance in distances:
            try:
                user_distance = get_object_or_404(UserDistance, user=user, distance=distance)
                if data['time_{}'.format(distance.id)]:
                    user_distance.pre_time = get_time_int(data['time_{}'.format(distance.id)])
                    user_distance.save()
                else:
                    user_distance.delete()
            except Http404:
                if data['time_{}'.format(distance.id)]:
                    UserDistance.objects.create(user=user,
                                                distance=distance,
                                                pre_time=get_time_int(data['time_{}'.format(distance.id)]),
                                                is_finished=True
                                                )

        return redirect('/competition/{}/user/distances/{}'.format(competition.pk, user.pk))

