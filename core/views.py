import json

from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.http import Http404
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404
from django.views.generic import TemplateView

from auth_main.models import User
from core.models import TeamRelationToUser, Invitations, Team


class UserListView(TemplateView):
    template_name = 'core/userlist.html'

    def get(self, request, *args, **kwargs):
        team = None
        try:
            team = get_object_or_404(TeamRelationToUser, user=request.user).team
        except Http404:
            pass

        user_list = User.objects.order_by('-created_at')
        paginator = Paginator(user_list, 25)
        page = request.GET.get('page', 1)

        try:
            users = paginator.page(page)
        except PageNotAnInteger:
            users = paginator.page(1)
        except EmptyPage:
            users = paginator.page(paginator.num_pages)

        return render(request, self.template_name, {'user': request.user, 'team': team, 'users': users})


class GetUserProfileView(TemplateView):
    template_name = 'core/user_profile.html'

    def get(self, request, *args, **kwargs):
        user = get_object_or_404(User, pk=kwargs['pk'])
        return render(request, self.template_name,
                      {'user': request.user, 'curr_user': user, 'is_teamlead': self.is_user_teamlead(request.user)})

    @staticmethod
    def is_user_teamlead(user):
        try:
            get_object_or_404(TeamRelationToUser, user=user, is_coach=True)
            return True
        except Http404:
            return False


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
        users = TeamRelationToUser.objects.filter(team=team)
        is_coach = users.filter(user=request.user).is_coach
        return render(request, self.template_name, {'team': team, 'users': users, 'is_coach': is_coach})
