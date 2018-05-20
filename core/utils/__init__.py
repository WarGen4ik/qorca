import textwrap
import zipfile

import pyqrcode
import requests
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.utils import translation
from django.utils.translation import gettext as _

from auth_main.models import User
from core.models import TeamRelationToUser, Team, UserDistance, CompetitionTeam, Distance


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


def querysetdistance_to_dict(users, competition):
    ret = list()
    for user in users:
        try:
            user = get_object_or_404(User, id=user['user'])
            user_distance = UserDistance.objects.filter(user=user, distance__competition=competition).all()[0]
            ret.append({'fullname': user.get_full_name(),
                        'location': user.profile.city,
                        'id': user.pk,
                        'is_finished': user_distance.is_finished})
        except Exception:
            pass

    return ret


from PIL import Image, ImageFont
from PIL import ImageDraw
from django.conf import settings
import os
import cyrtranslit


def getBadge(user, competition):
    try:
        team = TeamRelationToUser.objects.get(user=user).team
        CompetitionTeam.objects.get(team=team, competition=competition)
        team_name = team.name
    except:
        team_name = _('Single')

    distances = list()
    for distance in Distance.objects.filter(competition=competition).all():
        if UserDistance.objects.filter(user=user, distance=distance).exists():
            distances.append(distance)

    avatar_url = user.profile.avatar.url

    if not distances:
        return None

    r = requests.get(avatar_url, stream=True)
    if r.status_code == 200:
        with open(settings.BASE_DIR + '/tmp/{}'.format(avatar_url.split('/')[-1]), 'wb') as f:
            for chunk in r:
                f.write(chunk)

    avatar_url = settings.BASE_DIR + '/tmp/' + avatar_url.split('/')[-1]

    url = pyqrcode.create('https://qorca.herokuapp.com/core/user/{}'.format(user.id))

    url.png(settings.BASE_DIR + '/tmp/code.png', scale=10)
    qr = Image.open(settings.BASE_DIR + '/tmp/code.png', 'r')
    qr.thumbnail((200, 200), Image.ANTIALIAS)
    qr.save(settings.BASE_DIR + '/tmp/{}_qr.png'.format(user.id))
    qr = Image.open(settings.BASE_DIR + '/tmp/{}_qr.png'.format(user.id), 'r')

    avatar = Image.open(avatar_url, 'r')
    avatar.thumbnail((300, 300), Image.ANTIALIAS)
    avatar.save(settings.BASE_DIR + '/tmp/{}_avatar.png'.format(user.id))
    avatar = Image.open(settings.BASE_DIR + '/tmp/{}_avatar.png'.format(user.id), 'r')

    # background = Image.new('RGBA', (1024, 900), (255, 255, 255, 255))
    background = Image.open(settings.BASE_DIR + '/imgs/fon.png', 'r')
    draw = ImageDraw.Draw(background)
    bg_w, bg_h = background.size
    offset = (20, 770)
    background.paste(qr, offset)

    offset = (20, 220)
    background.paste(avatar, offset)

    font = ImageFont.truetype(settings.BASE_DIR + "/fonts/OpenSans-SemiBold.ttf", 35)
    fullname = user.get_full_name()
    if len(fullname) > 14:
        fullname = user.last_name + '\n' + user.first_name
    draw.text((360, 220), fullname, font=font, fill="black")
    font_small = ImageFont.truetype(settings.BASE_DIR + "/fonts/OpenSans-Regular.ttf", 30)
    font_competition_name = ImageFont.truetype(settings.BASE_DIR + "/fonts/OpenSans-SemiBoldItalic.ttf", 30)

    para = textwrap.wrap(competition.name, width=35)
    MAX_W, MAX_H = 700, 1000
    current_h, pad = 20, 3
    for line in para:
        w, h = draw.textsize(line, font=font_competition_name)
        draw.text(((MAX_W - w) / 2, current_h), line, font=font_competition_name, fill="black")
        current_h += h + pad

    draw.text((220, 150), 'MASTERS-ATHLETE', font=font_small, fill="black")

    draw.text((360, 340), team_name, font=font_competition_name, fill="black")
    font_tiny = ImageFont.truetype(settings.BASE_DIR + "/fonts/OpenSans-Regular.ttf", 25)
    font_day = ImageFont.truetype(settings.BASE_DIR + "/fonts/OpenSans-SemiBold.ttf", 25)
    draw.text((20, 700), _('Age group') + ': {}({})'.format(str(user.profile.get_age_group()), user.profile.get_age_group_numbers()), font=font_tiny, fill="black")
    draw.text((360, 500), _('Distances') + ':', font=font_small, fill="black")
    distances_1_text = ''
    distances_2_text = ''
    draw.text((360, 560), _('Day 1'), font=font_day, fill="black")
    i_1 = 1
    i_2 = 1
    for distance in distances:
        if distance.day == 1:
            distances_1_text += str(i_1) + '. ' + str(distance.length) + _(' m ') + distance.get_short_type_display() + '\n'
            i_1 += 1
        else:
            distances_2_text += str(i_2) + '. ' + str(distance.length) + _(' m ') + distance.get_short_type_display() + '\n'
            i_2 += 1

    draw.text((360, 590), distances_1_text, font=font_tiny, fill="black")
    if distances_2_text:
        draw.text((530, 560), _('Day 2'), font=font_day, fill="black")
        draw.text((530, 590), distances_2_text, font=font_tiny, fill="black")

    directory = settings.BASE_DIR + '/media/badges/{}'.format(competition.id)
    if not os.path.exists(directory):
        os.makedirs(directory)
    background.save(directory + '/{}_badge.png'.format(cyrtranslit.to_latin(user.get_full_name().replace(' ', '_'), 'ru')))

    for file in os.listdir(settings.BASE_DIR + '/tmp'):
        os.remove(settings.BASE_DIR + '/tmp/' + file)

    return directory + '/{}_badge.png'.format(cyrtranslit.to_latin(user.get_full_name().replace(' ', '_'), 'ru'))


def activate_language(session):
    if 'language' in session:
        translation.activate(session['language'])
    else:
        translation.activate(settings.LANGUAGE_CODE)
        session['language'] = settings.LANGUAGE_CODE


def get_archive(files_path, archive_path):
    zipf = zipfile.ZipFile(archive_path, 'w')
    for file in os.listdir(files_path):
        if '.zip' not in file:
            zipf.write(os.path.join(files_path, file), file)
    zipf.close()

    return archive_path


def get_all_badges(competition):
    directory = settings.BASE_DIR + '/media/badges/{}'.format(competition.id)
    if not os.path.exists(directory):
        os.makedirs(directory)
    users = UserDistance.objects.filter(distance__competition=competition).values('user').distinct()
    for user in users:
        user = User.objects.get(id=user['user'])
        if cyrtranslit.to_latin(user.get_full_name().replace(' ', '_'), 'ru') + '_badge.png' not in os.listdir(settings.BASE_DIR + '/media/badges/{}'.format(competition.id)):
            getBadge(user,competition,)
    return get_archive(settings.BASE_DIR + '/media/badges/{}'.format(competition.id), settings.BASE_DIR + '/media/badges/{}/badges.zip'.format(competition.id))


def delete_badge(user, competition):
    try:
        os.remove(settings.BASE_DIR + '/media/badges/{}/{}_badge.png'.format(competition.id, cyrtranslit.to_latin(user.get_full_name().replace(' ', '_'), 'ru')))
    except:
        pass