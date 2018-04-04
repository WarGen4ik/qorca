from django.shortcuts import render
from django.utils import translation
from django.utils.translation import gettext as _

from core.models import Competition
from core.utils import get_session_attributes, activate_language


def main(request, *args, **kwargs):
    activate_language(request.session)
    competitions = Competition.getLastCompetitions()
    opt = dict()
    opt['competitions'] = competitions
    if request.user.is_authenticated:
        opt.update({'gender': _('male') if request.user.profile.gender == 1 else _('female')})
        return render(request, 'core/index.html', dict(opt, **get_session_attributes(request)))
    else:
        return render(request, 'core/index.html', dict(opt, **get_session_attributes(request)))
