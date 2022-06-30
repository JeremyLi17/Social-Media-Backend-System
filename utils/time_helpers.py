from datetime import datetime
import pytz


def utc_now():
    # 此时返回的就是有时区信息的时间
    return datetime.now().replace(tzinfo=pytz.utc)