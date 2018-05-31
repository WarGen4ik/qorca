import datetime
import math


def foo(self):
    try:
        born = self
        today = datetime.date.today()
        age = today.year - born.year - 25
        if age < 0:
            return None
        groups = 'ABCDEFGHIJKLMN'
        age_group = groups[math.floor(age / 5)]
        return age_group
    except:
        return None


print(foo(datetime.datetime.strptime('1993-06-03', '%Y-%m-%d')))