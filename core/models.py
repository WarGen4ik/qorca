from django.db import models
import django.utils.timezone
from django.db.models import Q
from django.db.models import QuerySet
from django.http import Http404
from django.shortcuts import get_object_or_404

from auth_main.models import User


class Team(models.Model):
    name = models.CharField(max_length=150, unique=True)
    logo = models.ImageField(upload_to='logos/', default='logos/no-img.png')
    description = models.TextField(blank=True, default='')
    created_at = models.DateTimeField(default=django.utils.timezone.now)

    def is_user_teamlead(self, user):
        try:
            return get_object_or_404(TeamRelationToUser, user=user, team=self).is_coach
        except Http404:
            return False

    def __str__(self):
        return self.name


class TeamRelationToUser(models.Model):
    user = models.ForeignKey(User)
    team = models.ForeignKey(Team)
    is_coach = models.BooleanField(default=False)

    def __str__(self):
        return '{} in {}'.format(self.user.get_full_name(), self.team.name)


class Invitations(models.Model):
    from_user = models.ForeignKey(User, related_name='from_user')
    to_user = models.ForeignKey(User, related_name='to_user')
    team = models.ForeignKey(Team)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=django.utils.timezone.now)

    def __str__(self):
        return 'from {} to {}'.format(self.from_user.email, self.to_user.email)


class Competition(models.Model):
    REGIONS = (
        ('world', 'World'),
        ('europe', 'Europe'),
        ('ukraine', 'Ukraine'),
    )
    TRACKS = (
        (1, 1),
        (2, 2),
        (3, 3),
        (4, 4),
        (5, 5),
        (6, 6),
        (7, 7),
        (8, 8),
        (9, 9),
        (10, 10)
    )
    name = models.CharField(max_length=255)
    description = models.TextField()
    logo = models.ImageField(upload_to='competitions/logos/', default='competitions/logos/no-img.png')
    region = models.CharField(max_length=100, choices=REGIONS)
    track_count = models.SmallIntegerField(choices=TRACKS)
    started_at = models.DateField()
    created_at = models.DateTimeField(default=django.utils.timezone.now)

    def __str__(self):
        return self.name

    def getCountUsers(self):
        return CompetitionUser.objects.filter(competition=self).count()

    def getTeamsUsers(self):
        return CompetitionTeam.objects.filter(competition=self).count()

    @staticmethod
    def getLastCompetitions(length=6):
        result_query = QuerySet(Competition)
        for region in Competition.REGIONS:
            result_query = result_query | Competition.objects\
                                            .filter(started_at__gt=django.utils.timezone.now()) \
                                            .filter(region=region[0]) \
                                            .order_by('-started_at') \
                                            .all()[:length]

        return result_query.order_by('-started_at')

    def getDistances(self):
        return Distance.objects.filter(competition=self).all()


class CompetitionUser(models.Model):
    competition = models.ForeignKey(Competition)
    user = models.ForeignKey(User)
    created_at = models.DateTimeField(default=django.utils.timezone.now)


class CompetitionTeam(models.Model):
    competition = models.ForeignKey(Competition)
    team = models.ForeignKey(Team)
    created_at = models.DateTimeField(default=django.utils.timezone.now)


class Distance(models.Model):
    TYPES = (
        (1, 'Freestyle'),
        (2, 'Butterfly'),
        (3, 'Backstroke'),
        (4, 'Breaststroke'),
        (5, 'Dolphin kick'),
    )

    competition = models.ForeignKey(Competition, on_delete=models.CASCADE)
    distance_type = models.SmallIntegerField(choices=TYPES)
    length = models.SmallIntegerField()

    def __str__(self):
        return 'Competition: {} | Type: {} | Length: {}'.format(self.competition.name, self.get_distance_type_display(), self.length)


class UserDistance(models.Model):
    user = models.ForeignKey(User)
    distance = models.ForeignKey(Distance)
    time = models.TimeField()
