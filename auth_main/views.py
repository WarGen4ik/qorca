from django.contrib.auth import authenticate, logout, login
from django.db import IntegrityError
from django.http import Http404, HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import DetailView
from django.views.generic import TemplateView

from auth_main.models import User, Profile
from core.models import TeamRelationToUser, Invitations
from core.utils import get_session_attributes


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
                                            request.POST['psw'],
                                            )
            Profile.objects.create(user=user, city=request.POST['city'])
            login(request, user)
            request.session['alerts'] = [{'type': 'success', 'message': 'You have been registered successful.'}]
            return redirect('/')

        return render(request, self.template_name, {'error': 'Passwords are not equal each other.'})


class LoginView(TemplateView):
    template_name = 'auth_main/signin.html'

    def get(self, request, *args, **kwargs):
        try:
            next = request.environ['QUERY_STRING'].split('=')[1]
            if next:
                request.session['next'] = next
        except:
            pass
        return render(request, self.template_name)

    def post(self, request):
        user = authenticate(email=request.POST['email'], password=request.POST['psw'])
        if user is not None:
            login(request, user)

            try:
                request.session['team'] = get_object_or_404(TeamRelationToUser, user=request.user).team.pk
            except Http404:
                pass

            if 'next' in request.session:
                return redirect(request.session['next'])

            return redirect('/')
        return render(request, self.template_name)


class LogoutView(TemplateView):
    def get(self, request, *args, **kwargs):
        logout(request)
        return redirect('/')


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
            opt = {'user': request.user,
                   'teams_rel_user': teams_rel_user,
                   'invitations': invitations}
            return render(request, self.template_name, dict(opt, **get_session_attributes(request)))
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
