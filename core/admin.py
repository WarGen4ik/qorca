from django.contrib import admin

from core.models import TeamRelationToUser, Team, Invitations, Competition, CompetitionTeam, CompetitionUser, Distance

admin.site.register(TeamRelationToUser)
admin.site.register(Team)
admin.site.register(Invitations)
admin.site.register(Competition)
admin.site.register(CompetitionUser)
admin.site.register(CompetitionTeam)
admin.site.register(Distance)
