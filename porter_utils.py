from datetime import datetime, timedelta
from simulator.hospital import Hospital


current_time = lambda: datetime.now()


def deadline(created_time, window):
    return datetime.strptime(created_time, '%Y-%m-%d %H:%M:%S.%f') + timedelta(minutes=window)
