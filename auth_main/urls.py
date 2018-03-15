from django.conf import settings
from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^register$', views.RegisterView.as_view()),
    url(r'^login$', views.LoginView.as_view()),
    url(r'^logout$', views.LogoutView.as_view()),
    url(r'^profile$', views.ProfileView.as_view()),
]