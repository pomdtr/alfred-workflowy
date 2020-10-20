import sys
from parsedatetime import Calendar, Constants
import json
from datetime import datetime, timedelta

args = sys.argv[1:]
query = str.join(" ", args)
interval = query.split(":")

if len(interval) == 0:
    sys.exit(0)

calendar = Calendar(Constants(usePyICU=False))
result = ""
start, end = None, None
if len(interval) > 0:
    date = interval[0]
    date, ok = calendar.parse(date)
    if ok:
        result = datetime(*date[:3]).strftime("%Y-%m-%d")

        if len(interval) > 1:
            date = interval[1]
            date, ok = calendar.parse(date)
            if ok:
                end = datetime(*date[:3])
                end_excluded = end - timedelta(days=1)
                result_excluded = "%s -> %s" % (result, end_excluded.strftime("%Y-%m-%d"))

if not result:
    print(
        json.dumps(
            {"items": [{"title": "Please type a date", "valid": False}]}, indent=2
        )
    )
else:
    print(
        json.dumps(
            {"items": [{"title": result, "arg": result, "valid": True}]}, indent=2
        )
    )
