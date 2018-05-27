import datetime

time = datetime.timedelta(milliseconds=6544), '%M:%S.%f'
s = 6544

minutes, remainder = divmod(s, 6000)
seconds, mili = divmod(remainder, 100)


if minutes < 10:
    minutes = '0' + str(minutes)
else:
    minutes = str(minutes)

if seconds < 10:
    seconds = '0' + str(seconds)
else:
    seconds = str(seconds)

if mili < 10:
    mili = '0' + str(mili)
else:
    mili = str(mili)

print('{}:{}.{}'.format(minutes, seconds, mili))