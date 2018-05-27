import math

import time
from django.utils.translation import gettext as _
from decimal import Decimal, ROUND_HALF_UP

from competition.models import ResultPoints
from core.models import Distance, UserDistance, TeamRelationToUser, CompetitionTeam


def get_swim_params(swim_n, competition, day):
    result = list()
    stop_result = False
    index = 1
    distance_index = 1
    swim_index = 1
    for distance in Distance.objects.filter(competition=competition, day=day).all():
        for gender in range(2, 0, -1):
            not_end = True
            distance_swim_index = 1
            while not_end:
                users_distances = UserDistance.objects.filter(distance=distance, user__profile__gender=gender, is_finished=True) \
                                      .order_by('-time')[(
                                                         distance_swim_index - 1) * competition.track_count:distance_swim_index * competition.track_count]
                if not users_distances:
                    not_end = False
                    break

                for user_distance in users_distances:
                    try:
                        team = TeamRelationToUser.objects.filter(user=user_distance.user).first().team
                        CompetitionTeam.objects.get(team=team, competition=competition, is_complete=True)
                        team = team
                    except:
                        team = None

                    if not stop_result:
                        result.append(user_distance)

                if swim_index == swim_n:
                    stop_result = True
                elif not stop_result:
                    result.clear()
                index += 5
                swim_index += 1
                distance_swim_index += 1
        distance_index += 1

    return result, swim_index-1


def is_correct_time(time):
    if not time:
        return True

    try:
        minutes = int(time.split(':')[0])
        seconds = int(time.split(':')[1].split('.')[0])
        milisec = int(time.split('.')[1])
    except:
        return False

    if minutes > 59 or minutes < 0:
        return False

    if seconds > 59 or seconds < 0:
        return False

    if milisec > 99 or milisec < 0:
        return False

    return True


def get_points(distance, user, user_time, day, competition):
    type = distance.type
    length = distance.length
    pool_size = competition.pool_sizes.split(',')[day-1]

    try:
        rp = ResultPoints.objects.get(distance_type=type, distance_length=length, pool_size=pool_size, gender=user.profile.gender)
        time = float(rp.points.split(',')[user.profile.get_age_group_number()])
        user_time = get_time_float(user_time)
        return Decimal(1000 * math.pow((time/user_time), 3)).quantize(0, ROUND_HALF_UP)
    except:
        return 0


def get_time_float(time):
    minutes = int(time.split(':')[0])
    seconds = int(time.split(':')[1].split('.')[0])
    milisec = int(time.split('.')[1])

    res = 0.0
    res += milisec / 100
    res += seconds
    res += minutes * 60

    return res


def get_time_int(time):
    minutes = int(time.split(':')[0])
    seconds = int(time.split(':')[1].split('.')[0])
    milisec = int(time.split('.')[1])

    if minutes >= 60 or seconds >= 60:
        raise ValueError

    res = 0
    res += milisec
    res += seconds * 100
    res += minutes * 100 * 60

    return res


def time_to_str(timestamp):
    minutes, remainder = divmod(timestamp, 6000)
    seconds, mili = divmod(remainder, 100)

    if minutes < 10:
        minutes = '0' + str(minutes)
    else:
        minutes = str(minutes)

    if seconds < 10:
        seconds = '0' + str(seconds)
    else:
        seconds = str(seconds)

    if mili < 10:
        mili = '0' + str(mili)
    else:
        mili = str(mili)

    return '{}:{}.{}'.format(minutes, seconds, mili)