from django.shortcuts import render

from core.models import Competition
from core.utils import get_session_attributes


def main(request, *args, **kwargs):
    competitions = Competition.getLastCompetitions()
    opt = dict()
    opt['competitions'] = competitions
    if request.user.is_authenticated:
        opt.update({'gender': 'male' if request.user.profile.gender == 1 else 'female'})
        return render(request, 'core/index.html', dict(opt, **get_session_attributes(request)))
    else:
        return render(request, 'core/index.html', opt)
