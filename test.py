import datetime
from dateutil.relativedelta import relativedelta


def get_segments(start_date, end_date, interval_delta):
    curr_date = start_date
    segments = []

    while (curr_date <= end_date):

        curr_date = start_date + interval_delta
        segment = [start_date, curr_date - datetime.timedelta(days=1)]
        segments.append(segment)
        start_date = curr_date
        curr_date = start_date + interval_delta

    return segments

start_date = datetime.datetime(2022, 1, 1)
end_date = datetime.datetime(2022, 4, 1)


segments = get_segments(start_date, end_date, relativedelta(days=2,months=0,weeks=0))

for seg in segments:
    print(seg)