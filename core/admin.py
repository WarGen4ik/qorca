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
# admin.site.register(UserDistance)

admin.site.unregister(Group)


@admin.register(UserDistance)
class UserDistanceAdmin(admin.ModelAdmin):
    list_display = ['initials', 'day', 'type', 'length', 'pre_time']
    search_fields = ['user__last_name', 'user__first_name']

    def initials(self, obj):
        return obj.user.last_name + ' ' + obj.user.first_name
    initials.short_description = 'Ініціали'
    initials.admin_order_field = 'user__last_name'

    def day(self, obj):
        return obj.distance.day

    def type(self, obj):
        return obj.distance.get_type_display()

    def length(self, obj):
        return obj.distance.length
