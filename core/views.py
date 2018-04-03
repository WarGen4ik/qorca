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

from auth_main.models import User
from core.models import TeamRelationToUser, Invitations, Team, Competition, CompetitionUser, CompetitionTeam, Distance, \
    UserDistance
from core.utils import get_session_attributes, queryset_to_dict, getBadge
from core.widgets import CompetitionSelectWidget


class UserListView(TemplateView):
    template_name = 'core/userlist.html'

    def get(self, request, *args, **kwargs):

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
        user = User.objects.get(pk=kwargs['pk'])
        badge_path = getBadge(user.profile.avatar.url, user.get_full_name(), user.pk)
        file_wrapper = FileWrapper(open(badge_path, 'rb'))
        file_mimetype = mimetypes.guess_type(badge_path)
        response = HttpResponse(file_wrapper, content_type=file_mimetype)
        response['X-Sendfile'] = badge_path
        response['Content-Length'] = os.stat(badge_path).st_size
        response['Content-Disposition'] = 'attachment; filename={}'.format('{}\'s_badge.png'.format(user.get_full_name()).replace(' ', '_'))
        return response


class InvitationToTeamView(TemplateView):
    def post(self, request):
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
        if 'team' in request.session:
            return redirect('/core/teams/{}'.format(request.session['team'].name))

        opt = {}
        return render(request, self.template_name, dict(opt, **get_session_attributes(request)))

    def post(self, request):
        team = Team.objects.create(name=request.POST['name'],
                                   logo=request.FILES['logo'],
                                   description=request.POST['description'])
        TeamRelationToUser.objects.create(team=team, user=request.user, is_coach=True)
        request.session['team'] = team.pk
        request.session['alerts'] = [{'type': 'success', 'message': 'Team has been created!'}]
        return redirect('/core/teams/{}'.format(team.name))


class CompetitionView(TemplateView):
    template_name = 'core/competition.html'

    def get(self, request, *args, **kwargs):
        competition = Competition.objects.get(pk=kwargs['pk'])

        members_count = competition.getCountUsers()
        teams_count = competition.getTeamsUsers()
        distances = competition.getDistances()

        if request.user.is_authenticated:
            can_signup = dict()
            can_signup['user'] = not CompetitionUser.objects.filter(user=request.user, competition=competition).exists()
            if 'team' in request.session:
                can_signup['team'] = not CompetitionTeam.objects.filter(team__pk=request.session['team'],
                                                                        competition=competition).exists()

                if not can_signup['team']:
                    can_signup['user'] = 5

                can_signup['is_coach'] = TeamRelationToUser.objects.filter(user=request.user,
                                                                           is_coach=True).exists()
            else:
                can_signup['team'] = False

            opt = {'competition': competition,
                   'members_count': members_count,
                   'teams_count': teams_count,
                   'can_signup': can_signup,
                   'distances': distances,
                   'types': Distance.TYPES}
            return render(request, self.template_name, dict(opt, **get_session_attributes(request)))

        return render(request, self.template_name, {'competition': competition,
                                                    'members_count': members_count,
                                                    'teams_count': teams_count,
                                                    'distances': distances,
                                                    'types': Distance.TYPES})


class CompetitionSignUpUser(View):
    def post(self, request):
        data = json.loads(request.body.decode('utf-8'))
        competition = Competition.objects.get(pk=data['competition_id'])
        CompetitionUser.objects.get_or_create(competition=competition,
                                              user=request.user)

        return HttpResponse(200)


class CompetitionSignUpTeam(View):
    def post(self, request):
        data = json.loads(request.body.decode('utf-8'))
        try:
            competition = Competition.objects.get(pk=data['competition_id'])
            team = TeamRelationToUser.objects.get(user=request.user, is_coach=True).team
            CompetitionTeam.objects.get_or_create(competition=competition,
                                                  team=team)
        except:
            return HttpResponse(400)

        return HttpResponse(200)


class CompetitionSignOutUser(View):
    def post(self, request):
        data = json.loads(request.body.decode('utf-8'))
        competition = Competition.objects.get(pk=data['competition_id'])
        CompetitionUser.objects.filter(competition=competition,
                                       user=request.user).delete()

        return HttpResponse(200)


class CompetitionSignOutTeam(View):
    def post(self, request):
        data = json.loads(request.body.decode('utf-8'))
        try:
            competition = Competition.objects.get(pk=data['competition_id'])
            team = TeamRelationToUser.objects.get(user=request.user, is_coach=True).team
            CompetitionTeam.objects.filter(competition=competition,
                                           team=team).delete()
        except:
            return HttpResponse(400)

        return HttpResponse(200)


class CreateCompetitionView(TemplateView):
    template_name = 'core/create_competition.html'

    def get(self, request, *args, **kwargs):
        widget = CompetitionSelectWidget()
        return render(request, self.template_name, {'widget': widget, 'types': Distance.TYPES, 'range': range(10)})

    def post(self, request):
        competition = Competition.objects.create(
            name=request.POST['name'],
            description=request.POST['description'],
            logo=request.FILES['logo'],
            region=request.POST['region'],
            track_count=request.POST['tracks_count'],
            started_at=datetime.datetime.strptime(request.POST['started_at'], "%Y-%m-%d").date()
        )

        for i in range(10):
            if request.POST['length_' + str(i)]:
                Distance.objects.create(
                    competition=competition,
                    distance_type=request.POST['type_' + str(i)],
                    length=request.POST['length_' + str(i)],
                )
            else:
                break

        return redirect('/')


class RegisterCompetitionView(TemplateView):
    template_name = 'core/register_on_competition.html'

    def get(self, request, *args, **kwargs):
        competition = Competition.objects.get(pk=kwargs['pk'])
        distances = Distance.objects.filter(competition=competition).all()
        return render(request, self.template_name, {'types': Distance.TYPES,
                                                    'distances': distances,
                                                    'competition': competition})

    def post(self, request, *args, **kwargs):
        for x in range(10):
            time_name = 'time_{}'.format(x)
            if time_name in request.POST:
                distance = Distance.objects.get(pk=request.POST['distance_id_{}'.format(x)])
                UserDistance.objects.create(
                    distance=distance,
                    user=request.user,
                    time=request.POST[time_name]
                )

        return redirect('/')
