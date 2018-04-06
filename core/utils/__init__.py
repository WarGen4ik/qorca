import pyqrcode
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.utils import translation

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

    if request.user.is_authenticated:
        opt['user'] = request.user

    if 'team' in request.session:
        opt['team'] = Team.objects.filter(pk=request.session['team']).first()

    if 'alerts' in request.session:
        opt['alerts'] = request.session['alerts']
        del request.session['alerts']

    if 'language' in request.session:
        opt['language'] = request.session['language']
        print(request.session['language'])
    else:
        opt['language'] = 'en'

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


def getBadge(avatar_url, fullname, user, team_name, distances=None):
    url = pyqrcode.create('https://qorca.herokuapp.com/core/user/{}'.format(user.id))

    url.png(settings.BASE_DIR + '/tmp/code.png', scale=10)
    qr = Image.open(settings.BASE_DIR + '/tmp/code.png', 'r')
    qr.thumbnail((200, 200), Image.ANTIALIAS)
    qr.save(settings.BASE_DIR + '/tmp/{}_qr.png'.format(user.id))
    qr = Image.open(settings.BASE_DIR + '/tmp/{}_qr.png'.format(user.id), 'r')

    avatar = Image.open(settings.BASE_DIR + avatar_url, 'r')
    avatar.thumbnail((400, 400), Image.ANTIALIAS)
    avatar.save(settings.BASE_DIR + '/tmp/{}_avatar.png'.format(user.id))
    avatar = Image.open(settings.BASE_DIR + '/tmp/{}_avatar.png'.format(user.id), 'r')

    background = Image.new('RGBA', (1024, 900), (255, 255, 255, 255))
    draw = ImageDraw.Draw(background)
    bg_w, bg_h = background.size
    offset = (50, 570)
    background.paste(qr, offset)

    offset = (50, 50)
    background.paste(avatar, offset)

    font = ImageFont.truetype(settings.BASE_DIR + "/staticfiles/fonts/TitilliumWeb-Regular.ttf", 60)
    w, h = font.getsize(fullname)
    draw.text((500, 20), fullname, font=font, fill="black")
    draw.text((500, 100), team_name, font=font, fill="black")
    font_small = ImageFont.truetype(settings.BASE_DIR + "/staticfiles/fonts/TitilliumWeb-Regular.ttf", 40)
    draw.text((50, 500), 'Age group: \'' + str(user.profile.get_age_group()) + '\'', font=font_small, fill="black")
    # draw.text((500, 200), 'Distances:', font=font_small, fill="black")
    # distances_text = ''
    # i = 1
    # for distance in distances:
    #     distances_text += 'Distance №' + str(i) + '\n'
    #     i += 1
    #     distances_text += distance.type + ' - ' + str(distance.length) + ' m\n'
    #
    # draw.text((500, 260), distances_text, font=font_small, fill="black")
    background.save(settings.BASE_DIR + '/media/badges/{}_badge.png'.format(user.id))

    this_dir = settings.BASE_DIR + '/tmp/'
    for file in os.listdir(this_dir):
        os.remove(this_dir + file)

    return settings.BASE_DIR + '/media/badges/{}_badge.png'.format(user.id)


def activate_language(session):
    if 'language' in session:
        translation.activate(session['language'])


def get_age_group(birth_year):
    print(birth_year)
