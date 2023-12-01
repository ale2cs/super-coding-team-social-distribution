from datetime import datetime

def parse_iso8601_time(time_str):
    try:
        datetime_obj = datetime.fromisoformat(time_str)
    except ValueError:
        try:
            datetime_obj = datetime.strptime(time_str, "%Y-%m-%dT%H:%M:%S.%fZ")
        except ValueError:
            print("Invalid ISO 8601 format")
            return
    return datetime_obj.strftime("%b. %d, %Y, %I:%M %p")