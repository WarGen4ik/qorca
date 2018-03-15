from django.db import models
import django.utils.timezone
from auth_main.models import User


class Team(models.Model):
    name = models.CharField(max_length=150)
    logo = models.ImageField(upload_to='logos/', default='logos/no-img.png')

    def __str__(self):
        return self.name


class TeamRelationToUser(models.Model):
    user = models.ForeignKey(User)
    team = models.ForeignKey(Team)
    is_coach = models.BooleanField(default=False)


class Invitations(models.Model):
    from_user = models.ForeignKey(User, related_name='from_user')
    to_user = models.ForeignKey(User, related_name='to_user')
    team = models.ForeignKey(Team)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=django.utils.timezone.now)

    def __str__(self):
        return 'from {} to {}'.format(self.from_user.email, self.to_user.email)
