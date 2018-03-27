import json

from django.contrib.auth.decorators import login_required
from django.core import serializers
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import Q
from django.http import Http404
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.utils.decorators import method_decorator
from django.views import View
from django.views.generic import TemplateView

from auth_main.models import User
from core.models import TeamRelationToUser, Invitations, Team, Competition, CompetitionUser, CompetitionTeam
from core.utils import update_session, get_session_attributes, queryset_to_dict


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

        opt = {'curr_user': user, 'is_teamlead': is_teamlead}
        return render(request, self.template_name, dict(opt, **get_session_attributes(request)))


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
        TeamRelationToUser.objects.get_or_create(user=request.user, team=team)
        inv = Invitations.objects.get(to_user=request.user, team=team, is_active=True)
        inv.is_active = False
        inv.save()
        request.session['team'] = team
        return HttpResponse(status=200)


class InvitationDeclineView(TemplateView):
    def post(self, request):
        data = json.loads(request.body.decode('utf-8'))
        team = Team.objects.get(name=data['team_name'])
        inv = Invitations.objects.get(to_user=request.user, team=team, is_active=True)
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
        return redirect('/core/teams/{}'.format(team.name))


class CompetitionView(TemplateView):
    template_name = 'core/competition.html'

    def get(self, request, *args, **kwargs):
        competition = Competition.objects.get(pk=kwargs['pk'])

        members_count = competition.getCountUsers()
        teams_count = competition.getTeamsUsers()

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
                   'can_signup': can_signup, }
            return render(request, self.template_name, dict(opt, **get_session_attributes(request)))

        return render(request, self.template_name, {'competition': competition,
                                                    'members_count': members_count,
                                                    'teams_count': teams_count, })


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
