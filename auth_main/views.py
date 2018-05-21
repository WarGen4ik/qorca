from django.conf import settings
from django.contrib.auth import authenticate, logout, login
from django.core.mail import send_mail
from django.db import IntegrityError
from django.http import Http404, HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.views import View
from django.views.generic import DetailView
from django.views.generic import TemplateView
from django.utils.translation import gettext as _
from django.utils import translation

from auth_main.models import User, Profile, ContactMessage
from core.models import TeamRelationToUser, Invitations
from core.utils import get_session_attributes, activate_language


class RegisterView(TemplateView):
    template_name = 'auth_main/signup.html'

    def get(self, request, *args, **kwargs):
        activate_language(request.session)
        return render(request, self.template_name, get_session_attributes(request))

    def post(self, request):
        activate_language(request.session)
        if request.POST['psw'] == request.POST['psw-repeat']:
            try:
                get_object_or_404(User, email=request.POST['email'])
                request.session['alerts'] = [{'type': 'error', 'message': _('User with this email is already exist.')}]
                return render(request, self.template_name, get_session_attributes(request))
            except Http404:
                pass
            user = User.objects.create_user(request.POST['email'],
                                            request.POST['first_name'],
                                            request.POST['last_name'],
                                            request.POST['psw'],
                                            )
            Profile.objects.create(user=user, city=request.POST['city'])
            if not settings.DEBUG:
                with open(settings.BASE_DIR + '/auth_main/templates/email/email_confirm_{}.html'.format(translation.get_language())) as file:
                    link = request.build_absolute_uri() + '/verificate/' + user.profile.verification_code
                    send_mail('Q-ORCA email confirm', '',
                              settings.EMAIL_HOST_USER,
                              [user.email, ], fail_silently=settings.DEBUG,
                              html_message=file.read().replace('{link}', link))
            else:
                user.profile.is_verificated = True
                user.profile.save()
            request.session['alerts'] = [{'type': 'success', 'message': _('We have sent verification link to your email. Please, follow it to verificate your email. If there is no letter, please check "spam" in your email.')}]
            return redirect('/')
        request.session['alerts'] = [{'type': 'error', 'message': _('Passwords are not equal each other.')}]
        return render(request, self.template_name, get_session_attributes(request))


class LoginView(TemplateView):
    template_name = 'auth_main/signin.html'

    def get(self, request, *args, **kwargs):
        activate_language(request.session)
        opt = get_session_attributes(request)
        try:
            next = request.environ['QUERY_STRING'].split('=')[1]
            if next:
                request.session['next'] = next
        except:
            pass
        return render(request, self.template_name, opt)

    def post(self, request):
        activate_language(request.session)
        user = authenticate(email=request.POST['email'], password=request.POST['psw'])

        if user is not None:
            if not user.profile.is_verificated:
                request.session['alerts'] = [{'type': 'error', 'message': _('Please verificate your email to log in.')}]
                return redirect('/auth/verification/reset')
            login(request, user)

            try:
                request.session['team'] = get_object_or_404(TeamRelationToUser, user=request.user).team.pk
            except Http404:
                pass

            if 'next' in request.session:
                del request.session['next']
                return redirect(request.session['next'])

            return redirect('/')
        return redirect('/auth/login')


class LogoutView(TemplateView):
    def get(self, request, *args, **kwargs):
        activate_language(request.session)
        logout(request)
        return redirect('/')


class ProfileView(TemplateView):
    template_name = 'auth_main/profile.html'

    def get(self, request, *args, **kwargs):
        activate_language(request.session)
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
        activate_language(request.session)
        if request.user.is_authenticated:
            if 'city' in request.POST:
                data = dict()
                for x in request.POST:
                    data[x] = request.POST[x]
                try:
                    request.user.profile.update_data(**data)
                except ValueError:
                    opt = {'error': _('Wrong date format')}
                    return render(request, self.template_name, dict(opt, **get_session_attributes(request)))

                return redirect('/auth/profile')
            else:
                request.user.profile.avatar = request.FILES['img']
                request.user.profile.save()
                return HttpResponse()


class VerificateView(TemplateView):
    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            request.session['alerts'] = [{'type': 'success', 'message': _('You are already verificated')}]
            return redirect('/')

        try:
            profile = get_object_or_404(Profile, verification_code=kwargs['code'])
        except Http404:
            request.session['alerts'] = [{'type': 'error', 'message': _('Wrong verification code!')}]
            return redirect('/')
        if profile.is_verificated:
            request.session['alerts'] = [{'type': 'success', 'message': _('You are already verificated')}]
            return redirect('/')
        profile.is_verificated = True
        profile.save()

        login(request, profile.user)
        request.session['alerts'] = [{'type': 'success', 'message': _('Your email has been verificated')}]
        try:
            request.session['team'] = get_object_or_404(TeamRelationToUser, user=request.user).team.pk
        except Http404:
            pass
        return redirect('/')


class VerificateResetView(TemplateView):
    template_name = 'auth_main/reset_verification.html'

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            raise Http404

        return render(request, self.template_name)

    def post(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            raise Http404

        try:
            user = get_object_or_404(User, email=request.POST['email'])
        except Http404:
            request.session['alerts'] = [
                {'type': 'error', 'message': _('There is no user with this email.')}]
            return redirect(request.path)
        if user.profile.is_verificated:
            raise Http404

        user.profile.reset_code()

        with open(settings.BASE_DIR + '/auth_main/templates/email/email_confirm_{}.html'.format(
                translation.get_language())) as file:
            link = settings.BASE_URL + '/auth/register/verificate/' + user.profile.verification_code
            send_mail('Q-ORCA email confirm', '',
                      settings.EMAIL_HOST_USER,
                      [user.email, ], fail_silently=True,
                      html_message=file.read().replace('{link}', link))

        request.session['alerts'] = [{'type': 'success', 'message': _('We have sent verification link to your email. Please, follow it to verificate your email. If there is no letter, please check "spam" in your email/')}]
        return redirect('/')


class NewPasswordView(TemplateView):
    template_name = 'auth_main/reset_password_email.html'

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            raise Http404

        return render(request, self.template_name)

    def post(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            raise Http404

        user = get_object_or_404(User, email=request.POST['email'])
        if not user.profile.is_verificated:
            request.session['alerts'] = [
                {'type': 'error', 'message': _('You need to verificate your email.')}]
            return redirect('/')
        user.profile.reset_code()

        with open(settings.BASE_DIR + '/auth_main/templates/email/new_password_{}.html'.format(
                translation.get_language())) as file:
            link = settings.BASE_URL + '/auth/password/reset/' + user.profile.verification_code
            send_mail('Q-ORCA password reset', '',
                      settings.EMAIL_HOST_USER,
                      [user.email, ], fail_silently=True,
                      html_message=file.read().replace('{link}', link))

        request.session['alerts'] = [
            {'type': 'success', 'message': _('We have sent to you mail with instructions to reset your password.')}]

        return redirect('/')


class ResetPasswordView(TemplateView):
    template_name = 'auth_main/reset_password.html'

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            raise Http404

        profile = get_object_or_404(Profile, verification_code=kwargs['code'])
        if not profile.is_verificated:
            request.session['alerts'] = [
                {'type': 'error', 'message': _('You need to verificate your email.')}]
            return redirect('/')

        return render(request, self.template_name)

    def post(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            raise Http404

        profile = get_object_or_404(Profile, verification_code=kwargs['code'])
        if not profile.is_verificated:
            request.session['alerts'] = [
                {'type': 'error', 'message': _('You need to verificate your email.')}]
            return redirect('/')

        if request.POST['psw'] != request.POST['psw_r']:
            request.session['alerts'] = [
                {'type': 'error', 'message': _('Passwords are not equal each other.')}]
            return redirect(request.path)

        profile.user.set_password(request.POST['psw'])
        profile.user.save()
        profile.reset_code()

        request.session['alerts'] = [
            {'type': 'success', 'message': _('You have been changed your password.')}]

        return redirect('/auth/login')


class ContactView(View):
    def post(self, request, *args, **kwargs):
        activate_language(request.session)
        ContactMessage.objects.create(
            full_name=request.POST['name'],
            email=request.POST['email'],
            message=request.POST['message'],
        )

        request.session['alerts'] = [
            {'type': 'success', 'message': _('We will read your message as soon as possible.')}]

        return redirect('/')