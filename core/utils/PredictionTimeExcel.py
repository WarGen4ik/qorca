import openpyxl
from openpyxl.styles import *
from django.conf import settings
from django.utils.translation import gettext as _

from auth_main.models import User
from core.models import CompetitionUser, CompetitionTeam, TeamRelationToUser, Distance, UserDistance


class PredictionTimeExcel:
    def __init__(self, competition):
        self.competition = competition

    def create_excel(self):
        members = self.get_all_members()
        distances = Distance.objects.filter(competition=self.competition).all()
        members_distances = dict()
        for distance in distances:
            for member in members:
                if distance.id in members_distances:
                    members_distances[distance.id] = {
                        **members_distances[distance.id],
                        member.id: UserDistance.objects.filter(user=member, distance=distance).first()
                    }
                else:
                    members_distances[distance.id] = {
                        member.id: UserDistance.objects.filter(user=member, distance=distance).first()
                    }
            members_distances[distance.id] = sorted(
                members_distances[distance.id].items(),
                key=lambda distance_u: distance_u[1].time
            )

        wb = openpyxl.Workbook()
        ws = wb.active
        alf_index = 1
        index = 1
        distance_index = 1
        for distance in distances:
            char = self.get_char(alf_index - 1)
            next_char = self.get_char(alf_index)
            ws.merge_cells('{}{}:{}{}'.format(char, index, next_char, index))
            ws['{}{}'.format(char, index)].font = Font(size=14, bold=True)
            ws['{}{}'.format(char, index)] = _('Distance ') + '№{}'.format(distance_index)
            ws.column_dimensions[next_char].width = 15
            ws.column_dimensions[char].width = 15
            index += 1
            ws['{}{}'.format(char, index)] = _('Length:')
            ws['{}{}'.format(next_char, index)] = distance.length
            index += 1
            ws['{}{}'.format(char, index)] = _('Type:')
            ws['{}{}'.format(next_char, index)] = distance.get_type_display()
            index += 2
            border = Border(
                left=Side(border_style="thin", color='000000'),
                right=Side(border_style="thin", color='000000'),
                top=Side(border_style="thin", color='000000'),
                bottom=Side(border_style="thin", color='000000'),
                outline=Side(border_style="thin", color='000000')
            )
            ws['{}{}'.format(char, index)].border = border
            ws['{}{}'.format(char, index)].font = Font(bold=True)
            ws['{}{}'.format(next_char, index)].font = Font(bold=True)
            ws['{}{}'.format(next_char, index)].border = border
            ws['{}{}'.format(char, index)] = _('Member')
            ws['{}{}'.format(next_char, index)] = _('Prediction time')
            for member in members_distances[distance.id]:
                index += 1
                ws['{}{}'.format(char, index)].border = border
                ws['{}{}'.format(next_char, index)].border = border
                ws['{}{}'.format(char, index)] = User.objects.get(id=member[0]).get_full_name()
                ws['{}{}'.format(next_char, index)] = member[1].time

            alf_index += 3
            distance_index += 1
            index = 1

        path = settings.BASE_DIR + "/media/predictions/" + str(self.competition.id) + ".xlsx"
        wb.save(path)
        return path

    def get_char(self, index):
        alf = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
        try:
            return alf[index]
        except:
            index -= 26
            return 'A' + alf[index]

    def get_all_members(self):
        competition_rel_user = CompetitionUser.objects.filter(competition=self.competition).all()
        single_members = list()
        for rel in competition_rel_user:
            single_members.append(rel.user)

        teams = CompetitionTeam.objects.filter(competition=self.competition).all()
        team_members = list()

        for team in teams:
            rels = TeamRelationToUser.objects.filter(team=team.team).all()
            for rel in rels:
                team_members.append(rel.user)

        return single_members + list(set(team_members) - set(single_members))
