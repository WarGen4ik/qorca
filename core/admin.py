from django.contrib import admin
from django.contrib.auth.models import Group

from auth_main.models import ContactMessage
from core.models import TeamRelationToUser, Team, Invitations, Competition, CompetitionTeam, CompetitionUser, Distance, \
    RelayRace, RelayRaceTeam, UserDistance

admin.site.register(TeamRelationToUser)
admin.site.register(Team)
admin.site.register(Invitations)
admin.site.register(Competition)
admin.site.register(CompetitionUser)
admin.site.register(CompetitionTeam)
admin.site.register(Distance)
# admin.site.register(RelayRace)
# admin.site.register(RelayRaceTeam)
admin.site.register(ContactMessage)
admin.site.register(UserDistance)

admin.site.unregister(Group)