from django.db import models
import django.utils.timezone
from django.db.models import Q
from django.db.models import QuerySet
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.utils.translation import gettext_lazy as _

from auth_main.models import User


class Team(models.Model):
    name = models.CharField(_('Team name'), max_length=150, unique=True)
    logo = models.ImageField(_('Logo'), upload_to='logos/', default='logos/no-img.png')
    description = models.TextField(_('Description'), blank=True, default='')
    created_at = models.DateTimeField(_('Created at'), default=django.utils.timezone.now)

    def is_user_teamlead(self, user):
        try:
            return get_object_or_404(TeamRelationToUser, user=user, team=self).is_coach
        except Http404:
            return False

    def __str__(self):
        return self.name


class TeamRelationToUser(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    is_coach = models.BooleanField(_('Is coach'), default=False)

    def __str__(self):
        return '{} in {}'.format(self.user.get_full_name(), self.team.name)


class Invitations(models.Model):
    from_user = models.ForeignKey(User, related_name='from_user', on_delete=models.CASCADE)
    to_user = models.ForeignKey(User, related_name='to_user', on_delete=models.CASCADE)
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    is_active = models.BooleanField(_('Is active invitation'), default=True)
    created_at = models.DateTimeField(_('Created at'), default=django.utils.timezone.now)

    def __str__(self):
        return 'from {} to {}'.format(self.from_user.email, self.to_user.email)


class Competition(models.Model):
    REGIONS = (
        ('world', _('World')),
        ('europe', _('Europe')),
        ('ukraine', _('Ukraine')),
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
    name = models.CharField(_('Competition name'), max_length=255)
    count_days = models.SmallIntegerField(_('Count days'))
    description = models.TextField(_('Description'))
    logo = models.ImageField(_('Logo'), upload_to='competitions/logos/', default='competitions/logos/no-img.png')
    region = models.CharField(_('Region'), max_length=100, choices=REGIONS)
    track_count = models.SmallIntegerField(_('Count tracks'), choices=TRACKS)
    is_creating_finished = models.BooleanField(_('Is creating finished'), default=False)
    started_at = models.DateField(_('Started at'), )
    created_at = models.DateTimeField(_('Created at'), default=django.utils.timezone.now)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)

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
                                            .filter(is_creating_finished=True)\
                                            .filter(started_at__gt=django.utils.timezone.now()) \
                                            .filter(region=region[0]) \
                                            .order_by('-started_at') \
                                            .all()[:length]

        return result_query.order_by('-started_at')

    def getDistances(self, day):
        return Distance.objects.filter(competition=self, day=day).all()

    def getRelayRaces(self):
        return RelayRace.objects.filter(competition=self).all()

    def canUserRegister(self, user):
        if user.is_authenticated:
            if not CompetitionUser.objects.filter(user=user, competition=self, is_complete=True).exists():
                try:
                    team = get_object_or_404(TeamRelationToUser, user=user)
                    if not CompetitionTeam.objects.filter(team=team.team, competition=self).exists():
                        return 1
                except Http404:
                    return 1
            else:
                return -1

        return 0

    def canTeamRegister(self, team, user):
        if user.is_authenticated:
            team_rel_user = TeamRelationToUser.objects.get(team=team, user=user)
            if team_rel_user.is_coach:
                if not CompetitionTeam.objects.filter(team=team, competition=self, is_complete=True).exists():
                    team_rel_user = TeamRelationToUser.objects.get(team=team, user=user)
                    if team_rel_user.is_coach:
                        return 1
                else:
                    return -1

        return 0

    def canTeamRegisterRelay(self, team, user):
        if user.is_authenticated:
            team_rel_user = TeamRelationToUser.objects.get(team=team, user=user)
            if team_rel_user.is_coach:
                if not CompetitionTeam.objects.filter(team=team, competition=self, is_complete=True).exists():
                    team_rel_user = TeamRelationToUser.objects.get(team=team, user=user)
                    if team_rel_user.is_coach:
                        return 1
                else:
                    return -1

        return 0

    def unregisterSingleMembersFromTeam(self, team):
        for rel in team.teamrelationtouser_set.all():
            CompetitionUser.objects.filter(user=rel.user, competition=self).delete()

    def is_manager(self, user):
        if user.profile.role == 1:
            return False

        if self.created_by.id != user.id:
            return False
        return True


class CompetitionUser(models.Model):
    competition = models.ForeignKey(Competition, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(_('Created at'), default=django.utils.timezone.now)
    is_complete = models.BooleanField(_('Is user registration completed'), default=False)

    def __str__(self):
        return self.competition.name + ' | ' + self.user.get_full_name()


class CompetitionTeam(models.Model):
    competition = models.ForeignKey(Competition, on_delete=models.CASCADE)
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    created_at = models.DateTimeField(_('Created at'), default=django.utils.timezone.now)
    is_complete = models.BooleanField(_('Is team registration completed'), default=False)

    def __str__(self):
        return self.competition.name + ' | ' + self.team.name


class Distance(models.Model):
    TYPES = (
        (1, _('Freestyle')),
        (2, _('Butterfly')),
        (3, _('Backstroke')),
        (4, _('Breaststroke')), #brass
        (5, _('Dolphin kick')),
    )

    competition = models.ForeignKey(Competition, on_delete=models.CASCADE)
    type = models.SmallIntegerField(_('Distance type'), choices=TYPES)
    length = models.SmallIntegerField(_('Distance length'),)
    day = models.SmallIntegerField(_('Day number'))

    def __str__(self):
        return 'Competition: {} | Type: {} | Length: {}'.format(self.competition.name, self.get_type_display(), self.length)


class UserDistance(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    distance = models.ForeignKey(Distance, on_delete=models.CASCADE)
    time = models.CharField(_('Time for distance'), max_length=100)
    result_time = models.CharField(_('Result time'), max_length=100, default='')


class RelayRace(models.Model):
    TYPES = (
        (1, _('Mixed')),
        (2, _('Separated')),
    )
    length = models.IntegerField(_('Relay race length'))
    competition = models.ForeignKey(Competition, on_delete=models.CASCADE)
    count_members = models.SmallIntegerField(_('Count members'))
    day = models.SmallIntegerField(_('Day number'))
    type = models.SmallIntegerField(_('Distance type'), choices=TYPES)

    def __str__(self):
        return self.competition.name + ' | ' + self.get_type_display() + '/{}'.format(self.length)


class RelayRaceTeam(models.Model):
    name = models.CharField(_('Team for relay race'), max_length=255)
    relay_race = models.ForeignKey(RelayRace, on_delete=models.CASCADE)
    result_time = models.IntegerField(_('Result time'), default=0)
    time = models.IntegerField(_('Time for distance'),)

    def __str__(self):
        return self.relay_race.competition.name + ' | ' + self.name


class UserRelayRace(models.Model):
    team = models.ForeignKey(RelayRaceTeam, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)


# class PredictionFiles(models.Model):
#     competition = models.ForeignKey(Competition, on_delete=models.CASCADE)
#     file = models.FileField(upload_to='/predictions')
