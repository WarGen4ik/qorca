from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator

from core.models import TeamRelationToUser, Team


def update_session(session, user):
    if 'team' in session:
        return session

    try:
        session['team'] = get_object_or_404(TeamRelationToUser, user=user).team
    except Http404:
        pass
    finally:
        return session


def get_session_attributes(request):
    opt = dict()

    opt['user'] = request.user

    if 'team' in request.session:
        opt['team'] = Team.objects.filter(pk=request.session['team']).first()

    return opt
