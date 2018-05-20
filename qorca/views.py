from django.shortcuts import render
from django.utils import translation
from django.utils.translation import gettext as _

from auth_main.models import User
from core.models import Competition
from core.utils import get_session_attributes, activate_language


def main(request, *args, **kwargs):
    activate_language(request.session)
    competitions = Competition.getLastCompetitions()
    opt = dict()
    opt['competitions'] = competitions
    if request.user.is_authenticated:
        opt.update({'gender': _('male') if request.user.profile.gender == 1 else _('female')})
        request.user.profile.get_age_group()
        return render(request, 'core/index.html', dict(opt, **get_session_attributes(request)))
    else:
        return render(request, 'core/index.html', dict(opt, **get_session_attributes(request)))


def groups(request, *args, **kwargs):
    users = User.objects.all()
    for user in users:
        user.profile.age_group = user.profile.get_age_group_numbers()
        if user.profile.age_group is None:
            user.profile.age_group = ''
        user.profile.save()

    return None