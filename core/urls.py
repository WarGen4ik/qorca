from django.conf import settings
from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^users$', views.UserListView.as_view()),
    url(r'^user/(?P<pk>.+)$', views.GetUserProfileView.as_view()),
    url(r'^team/invitation$', views.InvitationToTeamView.as_view()),
    url(r'^team/invitation/accept$', views.InvitationAcceptView.as_view()),
    url(r'^team/invitation/decline$', views.InvitationDeclineView.as_view()),
    url(r'^teams/(?P<name>(.*))$', views.TeamView.as_view()),
]