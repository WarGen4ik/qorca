from django.conf import settings
from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^register$', views.RegisterView.as_view()),
    url(r'^verification/reset', views.VerificateResetView.as_view()),
    url(r'^register/verificate/(?P<code>(.*))$', views.VerificateView.as_view()),
    url(r'^password/reset/(?P<code>(.*))$', views.ResetPasswordView.as_view()),
    url(r'^new/password', views.NewPasswordView.as_view()),
    url(r'^login$', views.LoginView.as_view()),
    url(r'^logout$', views.LogoutView.as_view()),
    url(r'^profile$', views.ProfileView.as_view()),
    url(r'^contact$', views.ContactView.as_view()),
]