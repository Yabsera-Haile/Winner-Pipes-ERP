from datetime import datetime, tzinfo
import pytz
# Get current datetime in UTC
utc_now_dt = datetime.now(tz=pytz.UTC)
print('Current Datetime in UTC: ', utc_now_dt)
