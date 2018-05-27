from django.shortcuts import render
from django.utils import translation
from django.utils.translation import gettext as _

from auth_main.models import User
from competition.utils import get_time_int, time_to_str
from core.models import Competition, UserDistance
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
    users_distances = UserDistance.objects.all()

    for user_distance in users_distances:
        user_distance.pre_time = get_time_int(user_distance.time.strftime('%H:%M:%S'))
        user_distance.save()

    return None