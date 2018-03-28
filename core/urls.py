from django.conf import settings
from django.conf.urls import url
from django.contrib.auth.decorators import login_required

from . import views

urlpatterns = [
    url(r'^users$', views.UserListView.as_view()),
    url(r'^user/(?P<pk>.+)$', views.GetUserProfileView.as_view()),
    url(r'^download/badge/(?P<pk>.+)$', views.DownloadBadge.as_view()),

    url(r'^team/invitation$', views.InvitationToTeamView.as_view()),
    url(r'^team/invitation/accept$', views.InvitationAcceptView.as_view()),
    url(r'^team/invitation/decline$', views.InvitationDeclineView.as_view()),

    url(r'^teams/(?P<name>(.*))$', login_required(views.TeamView.as_view(), login_url=settings.LOGIN_REDIRECT_URL)),
    url(r'^create/team', views.CreateTeamView.as_view()),

    url(r'^competition/signup/user$', views.CompetitionSignUpUser.as_view()),
    url(r'^competition/signup/team$', views.CompetitionSignUpTeam.as_view()),
    url(r'^competition/signout/user$', views.CompetitionSignOutUser.as_view()),
    url(r'^competition/signout/team$', views.CompetitionSignOutTeam.as_view()),
    url(r'^competition/(?P<pk>(.+))$', views.CompetitionView.as_view()),
]