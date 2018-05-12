from django import forms
from django.utils.translation import ugettext_lazy as _

from core.models import Competition, Distance


class CompetitionSelectWidget(forms.Form):
    count_days = forms.ChoiceField(
        required=True,
        choices=[('1', '1'), ('2', '2')],
    )
    track_count = forms.ChoiceField(
        required=True,
        choices=Competition.TRACKS,
    )
    region = forms.ChoiceField(
        required=True,
        widget=forms.RadioSelect,
        choices=Competition.REGIONS,
    )
    region.label = _('Region')
    track_count.label = _('Count tracks')
    count_days.label = _('Count days')

