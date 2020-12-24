import caldav
from datetime import datetime, timezone
from decouple import config


def send_event(room, dt_start, dt_finish, username, password):
    client = caldav.DAVClient(url='https://caldav.yandex.ru/',
                              username=username, password=password)
    my_principal = client.principal()
    calendars = my_principal.calendars()

    now = datetime.now()
    date_now = now.strftime("%Y%m%d")
    time_now = now.strftime("%H%M%S")

    date = dt_start.astimezone(timezone.utc).strftime("%Y%m%d")
    start = dt_start.astimezone(timezone.utc).strftime("%H%M%S")
    finish = dt_finish.astimezone(timezone.utc).strftime("%H%M%S")

    message_events = f"""BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//Example Corp.//CalDAV Client//EN
BEGIN:VEVENT
UID:{date_now}T{time_now}Z-{username}
DTSTAMP:{date}T{start}Z
DTSTART:{date}T{start}Z
DTEND:{date}T{finish}Z
SUMMARY:Посетить "{room}"
END:VEVENT
END:VCALENDAR
"""
    calendars[0].save_event(message_events)


if __name__ == '__main__':
    username, password = 'test4864@yandex.ru', 'sihcmwvranazjwxo'
    
