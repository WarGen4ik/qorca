from django import forms
from django.utils.translation import gettext_lazy as _

from core.models import Competition, Distance


class CompetitionSelectWidget(forms.Form):
    tracks_count = forms.ChoiceField(
        required=True,
        choices=Competition.TRACKS,
    )
    region = forms.ChoiceField(
        required=True,
        widget=forms.RadioSelect,
        choices=Competition.REGIONS,
    )
    region.label = _('Region')
    tracks_count.label = _('Count tracks')

