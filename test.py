def get_time_int(time):
    minutes = int(time.split(':')[0])
    seconds = int(time.split(':')[1].split('.')[0])
    milisec = int(time.split('.')[1])

    if minutes >= 60 or seconds >= 60:
        raise ValueError

    res = 0
    res += milisec
    res += seconds * 100
    res += minutes * 100 * 60

    return res


def time_to_str(timestamp):
    minutes, remainder = divmod(timestamp, 6000)
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

    return '{}:{}.{}'.format(minutes, seconds, mili)

print(time_to_str(5000))