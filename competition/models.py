from django.db import models
from django.utils.translation import ugettext_lazy as _

from auth_main.models import Profile
from core.models import Distance


class ResultPoints(models.Model):
    pool_size = models.CharField(_('Pool size'), max_length=50)
    distance_length = models.SmallIntegerField(_('Distance length'))
    distance_type = models.SmallIntegerField(_('Distance type'), choices=Distance.TYPES)
    gender = models.SmallIntegerField(_('Gender'), choices=Profile.GENDER)
    points = models.TextField(_('Points'))

    def __str__(self):
        return 'Pool: {} m Distance: {} m {} {}'.format(
            self.pool_size,
            self.distance_length,
            self.get_distance_type_display(),
            self.get_gender_display()
        )
