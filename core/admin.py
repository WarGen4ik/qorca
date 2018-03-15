from django.contrib import admin

from core.models import TeamRelationToUser, Team, Invitations

admin.site.register(TeamRelationToUser)
admin.site.register(Team)
admin.site.register(Invitations)