from django.conf import settings
from django.conf.urls import url
from django.contrib.auth.decorators import login_required

from . import views

urlpatterns = [
    # url(r'^users$', views.UserListView.as_view()),
    # url(r'^user/(?P<pk>.+)$', views.GetUserProfileView.as_view()),
    # url(r'^download/badge/(?P<pk>.+)/(?P<comp>.+)$', views.DownloadBadge.as_view()),
    # url(r'^download/badges/(?P<comp>.+)$', views.DownloadAllBadges.as_view()),
    # url(r'^download/predictions/(?P<pk>.+)$', views.DownloadPredictions.as_view()),
    #
    # url(r'^team/invitation$', views.InvitationToTeamView.as_view()),
    # url(r'^team/invitation/accept$', views.InvitationAcceptView.as_view()),
    # url(r'^team/invitation/decline$', views.InvitationDeclineView.as_view()),
    #
    # url(r'^teams/(?P<name>(.*))$',
    #     login_required(views.TeamView.as_view(), login_url=settings.LOGIN_REDIRECT_URL)),
    # url(r'^create/team', views.CreateTeamView.as_view()),
    #
    # url(r'^language', views.ChangeLanguage.as_view()),
    #
    # url(r'^competition/confirm/(?P<pk>(.+))', views.ConfirmCompetitionView.as_view()),
    # url(r'^competition/create$', views.CreateCompetitionView.as_view()),
    # url(r'^competition/(?P<pk>(.+))/create/day/(?P<day>(.+))$',  views.CreateCompetitionDistancesView.as_view()),
    #
    # url(r'^competition/(?P<pk>(.+))/signup/single/(?P<day>(.+))/(?P<rel>(.+))$', views.RegisterCompetitionView.as_view()),
    # url(r'^competition/(?P<pk>(.+))/signout/single$', views.UnregisterCompetitionView.as_view()),
    # url(r'^competition/(?P<pk>(.+))/signup/team/(?P<day>(.+))/(?P<rel>(.+))', views.TeamRegisterCompetitionView.as_view()),
    # url(r'^competition/(?P<pk>(.+))/signout/team', views.TeamUnregisterCompetitionView.as_view()),
    #
    # url(r'^competition/(?P<pk>(.+))$', views.CompetitionView.as_view()),

    url(r'^(?P<pk>(.+))/list$', views.UserDistanceRegistrationView.as_view()),
    url(r'^(?P<pk>(.+))/find/users', views.FindUserView.as_view()),
    url(r'^(?P<pk>(.+))/finish/(?P<user_id>(.+))', views.FinishUserRegistrationView.as_view()),
    url(r'^(?P<pk>(.+))/remove/(?P<user_id>(.+))', views.RemoveUserRegistrationView.as_view()),

    url(r'^(?P<pk>(.+))/registration/finish', views.FinishCompetitionRegistration.as_view()),
    url(r'^(?P<pk>(.+))/registration/resume', views.ResumeCompetitionRegistration.as_view()),

    url(r'^(?P<pk>(.+))/swim/(?P<swim>(.+))/day/(?P<day>(.+))', views.SwimResultsView.as_view()),

    url(r'^(?P<pk>(.+))/download/results', views.DownloadResultsView.as_view()),
    url(r'^(?P<pk>(.+))/download/rating', views.DownloadRatingView.as_view()),

    url(r'^(?P<pk>(.+))/user/distances/(?P<user_id>(.+))', views.UserDistancesView.as_view()),
]
