from django.contrib import admin

from auth_main.models import ContactMessage
from core.models import TeamRelationToUser, Team, Invitations, Competition, CompetitionTeam, CompetitionUser, Distance, \
    RelayRace, RelayRaceTeam

admin.site.register(TeamRelationToUser)
admin.site.register(Team)
admin.site.register(Invitations)
admin.site.register(Competition)
admin.site.register(CompetitionUser)
admin.site.register(CompetitionTeam)
admin.site.register(Distance)
admin.site.register(RelayRace)
admin.site.register(RelayRaceTeam)
admin.site.register(ContactMessage)
