from django.shortcuts import render
from django.utils import translation
from django.utils.translation import gettext as _

from auth_main.models import User
from competition.utils import get_time_int, time_to_str
from core.models import Competition, UserDistance, Distance
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
    # distances = Distance.objects.filter(competition__id=1)
    # users = User.objects.all()
    #
    # for distance in distances:
    #     for user in users:
    #         if UserDistance.objects.filter(distance=distance, user=user).count() > 1:
    #             print(UserDistance.objects.filter(distance=distance, user=user).all())
    users = User.objects.filter(profile__age_group='')
    for user in users:
        print(user)



    return None