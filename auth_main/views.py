from django.contrib.auth import authenticate, logout, login
from django.db import IntegrityError
from django.http import Http404, HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import TemplateView
# from rest_framework import status
# from rest_framework.response import Response

from auth_main.models import User, Profile
from core.models import TeamRelationToUser, Invitations


class RegisterView(TemplateView):
    template_name = 'auth_main/signup.html'

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)

    def post(self, request):
        if request.POST['psw'] == request.POST['psw-repeat']:
            try:
                get_object_or_404(User, email=request.POST['email'])
                return render(request, self.template_name, {'error': 'User with this email is already exist.'})
            except Http404:
                pass
            user = User.objects.create_user(request.POST['email'],
                                            request.POST['first_name'],
                                            request.POST['last_name'],
                                            request.POST['psw'])
            Profile.objects.create(user=user, city=request.POST['city'])
            login(request, user)
            return redirect('/')
            # return render(request, self.template_name, {'status': 'success'})

        return render(request, self.template_name, {'error': 'Passwords are not equal each other.'})


class LoginView(TemplateView):
    template_name = 'auth_main/signin.html'

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)

    def post(self, request):
        user = authenticate(email=request.POST['email'], password=request.POST['psw'])
        if user is not None:
            login(request, user)

            # request.session['user'] = request.user
            # try:
            #     request.session['team_name'] = get_object_or_404(TeamRelationToUser, user=)
            # except Http404:
            #     pass
            return redirect('/')
        return render(request, self.template_name)


class LogoutView(TemplateView):
    def get(self, request, *args, **kwargs):
        logout(request)
        return render(request, 'core/index.html')


class ProfileView(TemplateView):
    template_name = 'auth_main/profile.html'

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            teams_rel_user = None
            try:
                teams_rel_user = TeamRelationToUser.objects.filter(user=request.user)
            except:
                pass

            invitations = Invitations.objects.filter(to_user=request.user, is_active=True).order_by('-created_at')
            return render(request, self.template_name, {'user': request.user, 'teams_rel_user': teams_rel_user, 'invitations': invitations})
        else:
            return redirect('/auth/login')

    def post(self, request):
        if request.user.is_authenticated:
            if 'city' in request.POST:
                data = dict()
                for x in request.POST:
                    data[x] = request.POST[x]
                try:
                    request.user.profile.update_data(**data)
                except ValueError:
                    return render(request, self.template_name, {'error': 'Wrong date format'})

                return redirect('/auth/profile')
            else:
                request.user.profile.avatar = request.FILES['img']
                request.user.profile.save()
                return HttpResponse()
