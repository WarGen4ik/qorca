import json
import mimetypes
import os
import datetime
from wsgiref.util import FileWrapper

from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import Q
from django.http import Http404
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.views import View
from django.views.generic import TemplateView
from django.utils.translation import gettext as _

from auth_main.models import User
from core.models import TeamRelationToUser, Invitations, Team, Competition, CompetitionUser, CompetitionTeam, Distance, \
    UserDistance, RelayRace, RelayRaceTeam, UserRelayRace
from core.utils import get_session_attributes, queryset_to_dict, getBadge, activate_language
from core.utils.PredictionTimeExcel import PredictionTimeExcel
from core.widgets import CompetitionSelectWidget


class UserListView(TemplateView):
    template_name = 'core/userlist.html'

    def get(self, request, *args, **kwargs):
        activate_language(request.session)
        user_list = User.objects.order_by('-created_at')
        paginator = Paginator(user_list, 20)
        page = request.GET.get('page', 1)

        try:
            users = paginator.page(page)
        except PageNotAnInteger:
            users = paginator.page(1)
        except EmptyPage:
            users = paginator.page(paginator.num_pages)

        opt = {'users': users}
        return render(request, self.template_name, dict(opt, **get_session_attributes(request)))

    def post(self, request):
        activate_language(request.session)
        data = json.loads(request.body.decode('utf-8'))
        search = data['search'].strip()
        if ' ' in search:
            search = search.split(' ')
            query = Q()
            for x in search:
                query = query | (Q(first_name__contains=x) | Q(last_name__contains=x))
            users = User.objects.filter(query).all()
        else:
            users = User.objects.filter(Q(first_name__contains=search) | Q(last_name__contains=search)).all()
        users_json = json.dumps(queryset_to_dict(users))
        return HttpResponse(users_json)


class GetUserProfileView(TemplateView):
    template_name = 'core/user_profile.html'

    def get(self, request, *args, **kwargs):
        activate_language(request.session)
        user = get_object_or_404(User, pk=kwargs['pk'])
        if 'team' in request.session:
            team = Team.objects.get(pk=request.session['team'])
            is_teamlead = team.is_user_teamlead(request.user)
        else:
            is_teamlead = False

        opt = {'curr_user': user, 'is_teamlead': is_teamlead,
               'site': 'https://immense-ocean-83797.herokuapp.com'}

        return render(request, self.template_name, dict(opt, **get_session_attributes(request)))


class DownloadBadge(View):
    def get(self, request, *args, **kwargs):
        activate_language(request.session)
        user = User.objects.get(pk=kwargs['pk'])
        competition = Competition.objects.get(pk=kwargs['comp'])
        try:
            team = TeamRelationToUser.objects.get(user=user).team
            CompetitionTeam.objects.get(team=team, competition=competition)
            team = team.name
        except:
            team = 'Single'

        distances = Distance.objects.filter(competition=competition).all()
        # distances = list()
        # for distance in Distance.objects.filter(competition=competition).all():
        #     distances.append(UserDistance.objects.get(user=user, distance=distance))

        badge_path = getBadge(user.profile.avatar.url, user.get_full_name(), user, team, distances)
        file_wrapper = FileWrapper(open(badge_path, 'rb'))
        file_mimetype = mimetypes.guess_type(badge_path)
        response = HttpResponse(file_wrapper, content_type=file_mimetype)
        response['X-Sendfile'] = badge_path
        response['Content-Length'] = os.stat(badge_path).st_size
        response['Content-Disposition'] = 'attachment; filename={}'.format(
            '{}\'s_badge.png'.format(user.get_full_name()).replace(' ', '_'))
        return response


class InvitationToTeamView(TemplateView):
    def post(self, request):
        activate_language(request.session)
        data = json.loads(request.body.decode('utf-8'))
        try:
            get_object_or_404(TeamRelationToUser,
                              user=User.objects.get(pk=data['user_id']),
                              team=TeamRelationToUser.objects.get(user=request.user, is_coach=True).team)
            return HttpResponse(status=400)
        except Http404:
            pass

        invitation, created = Invitations.objects.get_or_create(
            from_user=request.user,
            to_user=User.objects.get(pk=data['user_id']),
            team=TeamRelationToUser.objects.get(user=request.user, is_coach=True).team,
            is_active=True)

        if created:
            return HttpResponse(status=200)
        else:
            return HttpResponse(status=202)


class InvitationAcceptView(TemplateView):
    def post(self, request):
        activate_language(request.session)
        data = json.loads(request.body.decode('utf-8'))
        team = Team.objects.get(name=data['team_name'])
        try:
            get_object_or_404(TeamRelationToUser, user=request.user)
            return HttpResponse(status=401)
        except Http404:
            pass
        TeamRelationToUser.objects.get_or_create(user=request.user, team=team)
        inv = Invitations.objects.filter(to_user=request.user, team=team, is_active=True)
        if inv.exists():
            inv = inv.one()
        else:
            return HttpResponse(status=400)
        inv.is_active = False
        inv.save()
        request.session['team'] = team.pk
        return HttpResponse(status=200)


class InvitationDeclineView(TemplateView):
    def post(self, request):
        activate_language(request.session)
        data = json.loads(request.body.decode('utf-8'))
        team = Team.objects.get(name=data['team_name'])
        inv = Invitations.objects.filter(to_user=request.user, team=team, is_active=True)
        if inv.exists():
            inv = inv.one()
        else:
            return HttpResponse(status=400)
        inv.is_active = False
        inv.save()
        return HttpResponse(status=200)


class TeamView(TemplateView):
    template_name = 'core/team.html'

    def get(self, request, *args, **kwargs):
        activate_language(request.session)
        team = Team.objects.get(name=kwargs['name'])
        team_rel_users = TeamRelationToUser.objects.filter(team=team)
        is_coach = team_rel_users.filter(user=request.user).first().is_coach
        competitions_count = CompetitionTeam.objects.filter(team=team).count()
        opt = {'curr_team': team, 'team_rel_users': team_rel_users, 'is_coach': is_coach,
               'competitions': competitions_count, }
        return render(request, self.template_name, dict(opt, **get_session_attributes(request)))


class CreateTeamView(TemplateView):
    template_name = 'core/create-team.html'

    def get(self, request, *args, **kwargs):
        activate_language(request.session)
        if 'team' in request.session:
            return redirect('/core/teams/{}'.format(request.session['team'].name))

        opt = {}
        return render(request, self.template_name, dict(opt, **get_session_attributes(request)))

    def post(self, request):
        activate_language(request.session)
        team = Team.objects.create(name=request.POST['name'],
                                   logo=request.FILES['logo'],
                                   description=request.POST['description'])
        TeamRelationToUser.objects.create(team=team, user=request.user, is_coach=True)
        request.session['team'] = team.pk
        request.session['alerts'] = [{'type': 'success', 'message': _('Team has been created!')}]
        return redirect('/core/teams/{}'.format(team.name))


class CompetitionView(TemplateView):
    template_name = 'core/competition.html'

    def get(self, request, *args, **kwargs):
        activate_language(request.session)
        competition = Competition.objects.get(pk=kwargs['pk'])

        members_count = competition.getCountUsers()
        teams_count = competition.getTeamsUsers()
        distances = competition.getDistances(1)
        distances_second = None
        if competition.count_days == 2:
            distances_second = competition.getDistances(2)

        if request.user.is_authenticated:
            can_signup = dict()
            is_registed = False

            can_signup['user'] = competition.canUserRegister(request.user)
            if 'team' in request.session:
                team = Team.objects.filter(pk=request.session['team']).first()
                can_signup['team'] = competition.canTeamRegister(team, request.user)
                is_registed = CompetitionTeam.objects.filter(team=team, competition=competition).exists()
            else:
                try:
                    team = TeamRelationToUser.objects.filter(user=request.user).first().team
                    if team:
                        can_signup['team'] = competition.canTeamRegister(team, request.user)
                        is_registed = CompetitionTeam.objects.filter(team=team, competition=competition).exists()
                    else:
                        can_signup['team'] = 0
                except:
                    can_signup['team'] = 0

            if can_signup['user'] == -1:
                is_registed = True

            is_manager = competition.is_manager(request.user)

            opt = {'competition': competition,
                   'members_count': members_count,
                   'teams_count': teams_count,
                   'can_signup': can_signup,
                   'distances': distances,
                   'types': Distance.TYPES,
                   'distances_second': distances_second,
                   'is_registed': is_registed,
                   'is_manager': is_manager}
            return render(request, self.template_name, dict(opt, **get_session_attributes(request)))

        return render(request, self.template_name, {'competition': competition,
                                                    'members_count': members_count,
                                                    'teams_count': teams_count,
                                                    'distances': distances,
                                                    'types': Distance.TYPES,
                                                    'distances_second': distances_second, })


class CreateCompetitionView(TemplateView):
    template_name = 'core/create_competition.html'

    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated or request.user.profile.role == 1:
            raise Http404
        activate_language(request.session)
        widget = CompetitionSelectWidget()
        return render(request, self.template_name, {'widget': widget})

    def post(self, request):
        if not request.user.is_authenticated or request.user.profile.role == 1:
            raise Http404
        activate_language(request.session)
        competition = Competition.objects.create(
            name=request.POST['name'],
            description=request.POST['description'],
            logo=request.FILES['logo'],
            region=request.POST['region'],
            track_count=request.POST['track_count'],
            count_days=request.POST['count_days'],
            started_at=datetime.datetime.strptime(request.POST['started_at'], "%Y-%m-%d").date(),
            created_by=request.user,
        )

        return redirect('/core/competition/{}/create/day/1'.format(competition.pk))


class CreateCompetitionDistancesView(TemplateView):
    template_name = 'core/create_competition_distances.html'

    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated or request.user.profile.role == 1:
            raise Http404

        if int(kwargs['day']) not in [1, 2]:
            raise Http404

        competition = get_object_or_404(Competition, pk=kwargs['pk'])
        if competition.is_creating_finished:
            raise Http404
        activate_language(request.session)
        msg = _('Day ') + kwargs['day']
        return render(request, self.template_name, {
            'types': Distance.TYPES,
            'range': range(10),
            'day': msg,
            'is_first_day': int(kwargs['day']) == 1
        })

    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated or request.user.profile.role == 1:
            raise Http404

        if int(kwargs['day']) not in [1, 2]:
            raise Http404

        competition = get_object_or_404(Competition, pk=kwargs['pk'])
        if competition.is_creating_finished:
            raise Http404
        for i in range(10):
            if request.POST['length_' + str(i)]:
                Distance.objects.create(
                    competition=competition,
                    type=request.POST['type_' + str(i)],
                    length=request.POST['length_' + str(i)],
                    day=kwargs['day']
                )
            else:
                break

        if int(kwargs['day']) != competition.count_days:
            return redirect('/core/competition/{}/create/day/2'.format(competition.pk))
        else:
            competition.is_creating_finished = True
            competition.save()
            return redirect('/core/competition/{}'.format(competition.pk))


class RegisterCompetitionView(TemplateView):
    template_name = 'core/register_on_competition.html'

    def get(self, request, *args, **kwargs):
        activate_language(request.session)
        if not request.user.is_authenticated:
            return redirect('/')
        competition = get_object_or_404(Competition, pk=kwargs['pk'])

        if int(kwargs['day']) not in [1, 2]:
            raise Http404
        if not competition.is_creating_finished:
            raise Http404

        if competition.canUserRegister(request.user) == 1:
            distances = Distance.objects.filter(competition=competition, day=kwargs['day']).all()
            msg = _('Day ') + kwargs['day']
            return render(request, self.template_name, {'types': Distance.TYPES,
                                                        'distances': distances,
                                                        'competition': competition,
                                                        'day': msg,
                                                        'rel': kwargs['rel']})

        request.session['alerts'] = [
            {'type': 'error', 'message': _('You cannot register on this competition')}]

        return redirect('/')

    def post(self, request, *args, **kwargs):
        activate_language(request.session)
        if not request.user.is_authenticated:
            return redirect('/')
        competition = Competition.objects.get(pk=kwargs['pk'])
        if competition.canUserRegister(request.user) == 1:
            for x in range(10):
                time_name = 'time_{}'.format(x)
                if time_name in request.POST:
                    if request.POST[time_name]:
                        distance = Distance.objects.get(pk=request.POST['distance_id_{}'.format(x)])
                        UserDistance.objects.create(
                            distance=distance,
                            user=request.user,
                            time=request.POST[time_name],
                        )
            if int(kwargs['rel']) == 0:
                obj = CompetitionUser.objects.create(user=request.user, competition=competition)
            else:
                obj = get_object_or_404(CompetitionUser, pk=kwargs['rel'])
        else:
            request.session['alerts'] = [
                {'type': 'error', 'message': _('You have been already registrated on this competition!')}]
            return redirect('/core/competition/{}'.format(competition.pk))

        if int(kwargs['day']) != competition.count_days:
            return redirect('/core/competition/{}/signup/single/2/{}'.format(competition.pk, obj.pk))
        else:
            obj.is_complete = True
            obj.save()
            request.session['alerts'] = [{'type': 'success', 'message': _('You have been registrated successful!')}]
            return redirect('/core/competition/{}'.format(competition.pk))


class UnregisterCompetitionView(View):
    def post(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            competition = Competition.objects.get(pk=kwargs['pk'])
            if competition.canUserRegister(request.user) == -1:
                CompetitionUser.objects.filter(user=request.user, competition=competition).delete()
                for distance in Distance.objects.filter(competition=competition).all():
                    UserDistance.objects.filter(user=request.user, distance=distance).delete()
            request.session['alerts'] = [{'type': 'success', 'message': _('You have been unregistrated successful!')}]

        return redirect('/')


class TeamRegisterCompetitionView(TemplateView):
    template_name = 'core/team_register_on_competition.html'

    def get(self, request, *args, **kwargs):
        activate_language(request.session)
        if not request.user.is_authenticated:
            return redirect('/')
        competition = get_object_or_404(Competition, pk=kwargs['pk'])
        if int(kwargs['day']) not in [1, 2]:
            raise Http404
        if not competition.is_creating_finished:
            raise Http404
        if 'team' in request.session:
            team = Team.objects.filter(pk=request.session['team']).first()
        else:
            team = TeamRelationToUser.objects.get(user=request.user).team
        if competition.canTeamRegister(team, request.user) == 1:
            msg = _('Day ') + kwargs['day']
            users = TeamRelationToUser.objects.filter(team=team).all()
            distances = Distance.objects.filter(competition=competition, day=kwargs['day']).all()
            return render(request, self.template_name, {'types': Distance.TYPES,
                                                        'distances': distances,
                                                        'competition': competition,
                                                        'users': users,
                                                        'day': msg})

        request.session['alerts'] = [
            {'type': 'error', 'message': _('You cannot register team on this competition')}]

        return redirect('/')

    def post(self, request, *args, **kwargs):
        activate_language(request.session)
        if not request.user.is_authenticated:
            return redirect('/')
        competition = get_object_or_404(Competition, pk=kwargs['pk'])
        if int(kwargs['day']) not in [1, 2]:
            raise Http404
        if not competition.is_creating_finished:
            raise Http404
        if 'team' in request.session:
            team = Team.objects.filter(pk=request.session['team']).first()
        else:
            team = TeamRelationToUser.objects.get(user=request.user).team
        if competition.canTeamRegister(team, request.user) == 1:
            competition.unregisterSingleMembersFromTeam(team)
            users = TeamRelationToUser.objects.filter(team=team).all()
            for user in users:
                for x in range(10):
                    time_name = 'time_{}-{}'.format(x, user.user.pk)
                    if time_name in request.POST:
                        if request.POST[time_name]:
                            distance = Distance.objects.get(pk=request.POST['distance_id_{}'.format(x)])
                            UserDistance.objects.create(
                                distance=distance,
                                user=user.user,
                                time=request.POST[time_name]
                            )
            if int(kwargs['rel']) == 0:
                obj = CompetitionTeam.objects.create(team=team, competition=competition)
            else:
                obj = get_object_or_404(CompetitionTeam, pk=kwargs['rel'])
        else:
            request.session['alerts'] = [
                {'type': 'error', 'message': _('Your team has been already registrated on this competition!')}]
            return redirect('/core/competition/{}'.format(competition.pk))

        if int(kwargs['day']) != competition.count_days:
            return redirect('/core/competition/{}/signup/team/2/{}'.format(competition.pk, obj.pk))
        else:
            obj.is_complete = True
            obj.save()
            request.session['alerts'] = [{'type': 'success', 'message': _('You have been registrated successful!')}]
            return redirect('/core/competition/{}'.format(competition.pk))


class TeamUnregisterCompetitionView(View):
    def post(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            if 'team' in request.session:
                team = Team.objects.filter(pk=request.session['team']).first()
            else:
                team = TeamRelationToUser.objects.get(user=request.user).team
            competition = Competition.objects.get(pk=kwargs['pk'])
            if competition.canTeamRegister(team, request.user) == -1:
                CompetitionTeam.objects.filter(team=team, competition=competition).delete()
                for rel in TeamRelationToUser.objects.filter(team=team).all():
                    for distance in Distance.objects.filter(competition=competition).all():
                        UserDistance.objects.filter(user=rel.user, distance=distance).delete()
            request.session['alerts'] = [
                {'type': 'success', 'message': _('Your team has been unregistrated successful!')}]

        return redirect('/')


class ChangeLanguage(View):
    def get(self, request, *args, **kwargs):
        if 'language' in request.GET:
            request.session['language'] = request.GET['language']
        return redirect(request.GET['next'])


class DownloadPredictions(View):
    def get(self, request, *args, **kwargs):
        competition = Competition.objects.get(pk=kwargs['pk'])
        if competition.is_manager(request.user):
            path = PredictionTimeExcel(competition).create_excel()
            if path is None:
                return
            file_wrapper = FileWrapper(open(path, 'rb'))
            file_mimetype = mimetypes.guess_type(path)
            response = HttpResponse(file_wrapper, content_type=file_mimetype)
            response['X-Sendfile'] = path
            response['Content-Length'] = os.stat(path).st_size
            response['Content-Disposition'] = 'attachment; filename={}'.format(
                '{}\'s_predictions.xlsx'.format(competition.name).replace(' ', '_'))
            return response

        raise Http404


class ConfirmCompetitionView(View):
    def post(self, request, *args, **kwargs):
        competition = get_object_or_404(Competition, pk=kwargs['pk'])
        competition.is_creating_finished = True
        competition.save()
        return HttpResponse(status=200)
