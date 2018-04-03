import pyqrcode
from django.http import Http404
from django.shortcuts import get_object_or_404

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

    if 'alerts' in request.session:
        opt['alerts'] = request.session['alerts']
        del request.session['alerts']

    return opt


def queryset_to_dict(users):
    ret = list()
    for user in users:
        try:
            ret.append({'fullname': user.get_full_name(),
                        'location': user.profile.city,
                        'id': user.pk})
        except Exception:
            pass

    return ret


from PIL import Image, ImageFont
from PIL import ImageDraw
from django.conf import settings
import os


def getBadge(avatar_url, fullname, id):
    url = pyqrcode.create('https://qorca.herokuapp.com/core/user/{}'.format(id))

    url.png(settings.BASE_DIR + '/tmp/code.png', scale=10)
    qr = Image.open(settings.BASE_DIR + '/tmp/code.png', 'r')
    qr.thumbnail((400, 400), Image.ANTIALIAS)
    qr.save(settings.BASE_DIR + '/tmp/{}_qr.png'.format(id))
    qr = Image.open(settings.BASE_DIR + '/tmp/{}_qr.png'.format(id), 'r')

    avatar = Image.open(settings.BASE_DIR + avatar_url, 'r')
    avatar.thumbnail((400, 400), Image.ANTIALIAS)
    avatar.save(settings.BASE_DIR + '/tmp/{}_avatar.png'.format(id))
    avatar = Image.open(settings.BASE_DIR + '/tmp/{}_avatar.png'.format(id), 'r')

    background = Image.new('RGBA', (1024, 670), (255, 255, 255, 255))
    draw = ImageDraw.Draw(background)
    bg_w, bg_h = background.size
    offset = (bg_w - 450, (bg_h - 400) // 2)
    background.paste(qr, offset)

    offset = (50, (bg_h - 400) // 2)
    background.paste(avatar, offset)

    font = ImageFont.truetype(settings.BASE_DIR + "/staticfiles/fonts/TitilliumWeb-Regular.ttf", 60)
    w, h = font.getsize(fullname)
    draw.text(((bg_w - w) / 2, 20), fullname, font=font, fill="black")
    background.save(settings.BASE_DIR + '/media/badges/{}_badge.png'.format(id))

    this_dir = settings.BASE_DIR + '/tmp/'
    for file in os.listdir(this_dir):
        os.remove(this_dir + file)

    return settings.BASE_DIR + '/media/badges/{}_badge.png'.format(id)
