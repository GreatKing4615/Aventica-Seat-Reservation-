from MainApp.models import *
# from django.contrib.auth.models import Group, User
from datetime import timedelta, datetime, timezone
import pytz
# import os
from random import choice


def clear_users():
    for i in User.objects.all():
        if not i.is_superuser:
            i.delete()


def clear_workplaces():
    for i in Workplace.objects.all():
        i.delete()


def clear_meeting_rooms():
    for i in Meeting_Room.objects.all():
        i.delete()


def clear_workplaces_schedule():
    for i in Workplace_Schedule.objects.all():
        i.delete()


def clear_meeting_rooms_schedule():
    for i in Meeting_Room_Schedule.objects.all():
        i.delete()


def clear_all():
    clear_users()
    clear_workplaces()
    clear_meeting_rooms()


def timezone_from_utcoffset(str_utcoffset):
    if str_utcoffset == 'UTC+02:00':
        return pytz.timezone('Europe/Kaliningrad')
    if str_utcoffset == 'UTC+03:00':
        return pytz.timezone('Europe/Moscow')
    if str_utcoffset == 'UTC+04:00':
        return pytz.timezone('Europe/Volgograd')
    if str_utcoffset == 'UTC+05:00':
        return pytz.timezone('Asia/Yekaterinburg')
    if str_utcoffset == 'UTC+06:00':
        return pytz.timezone('Asia/Omsk')
    if str_utcoffset == 'UTC+07:00':
        return pytz.timezone('Asia/Krasnoyarsk')
    if str_utcoffset == 'UTC+08:00':
        return pytz.timezone('Asia/Irkutsk')
    if str_utcoffset == 'UTC+09:00':
        return pytz.timezone('Asia/Yakutsk')
    if str_utcoffset == 'UTC+10:00':
        return pytz.timezone('Asia/Vladivostok')
    if str_utcoffset == 'UTC+11:00':
        return pytz.timezone('Asia/Sakhalin')
    if str_utcoffset == 'UTC+12:00':
        return pytz.timezone('Asia/Kamchatka')
    return None


def place_strings(queryset, place_type):
    strings = []
    for row in queryset:
        place_name = row.name
        place_id = row.id
        res = {'place_name': place_name}
        res['place_id'] = place_id
        strings.append(res)
    return strings


def place_shedule_strings(queryset, place_type):
    strings = []
    for row in queryset:
        try:
            user_tz = row.user.user_preferences.timezone
        except Exception:
            strings.append(f'User {row.user} has no User_preferences!')
            continue
        start = row.start.time().strftime('%H:%M')
        finish = row.finish.time().strftime('%H:%M')
        schedule_id=row.id
        if place_type == 'Workplace':
            place_id = row.workplace_id
            place_name = row.workplace.name
        elif place_type == 'Meeting Room':
            place_id = row.meeting_room_id
            place_name = row.meeting_room.name

        res = {'place_type': place_type, 'place_name': place_name, 'place_id': place_id,
               'date': row.start.date().strftime('%d/%m/%y'), 'start': start, 'finish': finish,
               'username': row.user.username, 'timezone': user_tz, 'schedule_id':schedule_id}
        # res = f'{place_type}#{place_id} at {row.start.date()} from {start} to {finish} by {row.user.username}, {user_tz}'
        strings.append(res)
    return strings


def check_place_schedule(place_id, str_utcoffset, start, finish, place_type='Room'):
    '''
    param room_id (int)
    param str_utcoffset offset in form 'UTC+03:00'
    param date_
    param start (local datetime)
    param finish (local datetime)
    Test this as check_schedule(...)[0], since return value is a tuple!
    '''
    print(
        f'Checking for {place_type}#{place_id}, {start.strftime("%d/%m/%y %H:%M")}, {finish.strftime("%d/%m/%y %H:%M")}')
    tz = timezone_from_utcoffset(str_utcoffset)
    if not tz:
        return (False, f"Invalid utc offset: {str_utcoffset}")

    if start.date() not in [(datetime.utcnow().astimezone(tz) + timedelta(days=x)).date() for x in range(15)]:
        return (False, f"Invalid date boundaries, should be from <today> to <today + 14 days>")

    if place_type == 'Workplace':
        try:
            if not Workplace.objects.filter(pk=place_id).exists():
                return (False, "No such Workplace")

            rows = Workplace_Schedule.objects.filter(workplace_id=place_id)

        except ValueError:
            return (False, f"Invalid Workplace id: {place_id}")

    elif place_type == 'Room':
        try:
            if not Meeting_Room.objects.filter(pk=place_id).exists():
                return (False, "No such Meeting room")

            rows = Meeting_Room_Schedule.objects.filter(
                meeting_room_id=place_id)

        except ValueError:
            return (False, f"Invalid Meeting room id: {place_id}")

    else:
        return (False, f"Wrong place_type: {place_type}")

    if start.date() != finish.date():
        return (False, "Start and finish not on the same day")

    if start >= finish:
        return (False, "start >= finish")

    if start.hour < 9 or (finish.hour >= 22 and finish.minute > 0):
        return (False, "Invalid time boundaries, should be from 09:00 to 22:00")

    if not rows:
        return (True, "Whole day was free")

    # print(f'Local start is {start.strftime("%d/%m/%y %H:%M")}, local finish is {finish.strftime("%d/%m/%y %H:%M")}')
    start, finish = start.astimezone(
        timezone.utc), finish.astimezone(timezone.utc)
    # print(f'UTC start is {start.strftime("%d/%m/%y %H:%M")}, UTC finish is {finish.strftime("%d/%m/%y %H:%M")}')

    for row in rows:
        # print(f'start is {row.start.time().strftime("%d/%m %H:%M")}UTC, finish is {row.finish.time().strftime("%d/%m %H:%M")}UTC')
        if row.start <= start <= row.finish:
            if start != row.finish:
                return (False, f"1.Occupied by {row.user.first_name}, {row.user.last_name} from {row.start.time().strftime('%H:%M')}UTC"
                               f" to {row.finish.time().strftime('%H:%M')}UTC!")

        if row.start <= finish <= row.finish:
            if finish != row.start:
                return (False, f"2.Occupied by {row.user.first_name}, {row.user.last_name} from {row.start.time().strftime('%H:%M')}UTC"
                               f" to {row.finish.time().strftime('%H:%M')}UTC!")

        if start <= row.start and finish >= row.finish:
            return (False, f"3.Occupied by {row.user.first_name}, {row.user.last_name} from {row.start.time().strftime('%H:%M')}UTC"
                           f" to {row.finish.time().strftime('%H:%M')}UTC!")

    return (True, "Free")


def fill():
    # call_command('makemigrations')
    # call_command('migrate')
    # clear_all()
    # print('filled!!!')

    user = User.objects.create_user(
        username='User1', password='User1', email='example@aventica.ru')
    user_prefs = User_preferences.objects.create(
        user=user, timezone='Asia/Yekaterinburg, UTC+05:00')
    user_msc = User.objects.create_user(
        username='User2', password='User2', email='example2@aventica.ru')
    user_msc_prefs = User_preferences.objects.create(
        user=user_msc, timezone='Europe/Moscow, UTC+03:00')

    # for i in range(5):
    wp1 = Workplace.objects.create(name=f'Рабочее место у окна',
                                   description="Светлое рабочее пространство, с видом на парк"),
    wp2 = Workplace.objects.create(name=f'Рабочее место в опенспейсе',
                                   description="Есть возможность поработать в команде :)"),
    wp3 = Workplace.objects.create(name=f'Рабочее место для курильщиков', description="Ближе всех к выходу"),
    wp4 = Workplace.objects.create(name=f'Рабочее место рядом с куллером', description="Для тех, кого мучает жажда"),
    wp5 = Workplace.objects.create(name=f'Рабочее место рядом с приставкой',
                                   description="""Для тех, кто пришел "поработать" """)

    mr1 = Meeting_Room.objects.create(
        name='Центральная переговорная комната', capacity=20, description="С проектором и ВКС")
    mr2 = Meeting_Room.objects.create(
        name='Комната для брейнштормов', capacity=10,
        description="Панорамные окна, система кондиционирования и кресла-мешки")

    workplaces = Workplace.objects.all()
    print(workplaces)

    for i in range(100):
        days = choice([x for x in range(15)])
        hours = choice([x for x in range(24)])
        u = choice([user, user_msc])
        timezone = pytz.timezone(u.user_preferences.timezone.split(',')[0])
        str_utcoffset = u.user_preferences.timezone.split(',')[-1].strip()
        start = datetime.now().astimezone(timezone) + \
                timedelta(days=days, hours=hours)
        hours = choice([x for x in range(24)])
        finish = start + timedelta(hours=hours)
        wp = choice([wp1,wp2,wp3,wp4,wp5])
        res, cause = check_place_schedule(
            wp.id, str_utcoffset, start, finish, 'Workplace')
        if res:
            Workplace_Schedule.objects.create(
                workplace=wp, start=start, finish=finish, user=u)
        else:
            print(
                f'Failed because {cause}')

    for i in range(100):
        days = choice([x for x in range(15)])
        hours = choice([x for x in range(24)])
        u = choice([user, user_msc])
        timezone = pytz.timezone(u.user_preferences.timezone.split(',')[0])
        str_utcoffset = u.user_preferences.timezone.split(',')[-1].strip()
        start = datetime.utcnow().astimezone(timezone) + \
                timedelta(days=days, hours=hours)
        hours = choice([x for x in range(24)])
        finish = start + timedelta(hours=hours)
        mr = choice([mr1, mr2])
        res, cause = check_place_schedule(
            mr.id, str_utcoffset, start, finish, 'Room')
        if res:
            Meeting_Room_Schedule.objects.create(
                meeting_room=mr, start=start, finish=finish, user=u)
        else:
            print(
                f'Failed because {cause}')


def prep():
    clear_all()
    fill()
    wps = Workplace_Schedule.objects.all().order_by('start')
    # mrs = Meeting_Room_Schedule.objects.all().order_by('start')
    # mr = Meeting_Room.objects.all()[0]
    # for i in mrs:
    #     timezone = pytz.timezone(i.user.user_preferences.timezone.split(',')[0])
    #     print(
    #         (f'MR {i.meeting_room}'
    #          f'{i.start.astimezone(timezone).strftime("%d-%m-%y %H:%M %z")}'
    #          f'to {i.finish.astimezone(timezone).strftime("%d-%m-%y %H:%M %z")}'))

    for i in wps:
        timezone = pytz.timezone(
            i.user.user_preferences.timezone.split(',')[0])
        print(
            (f'MR {i.workplace}'
             f'{i.start.astimezone(timezone).strftime("%d-%m-%y %H:%M %z")}'
             f'to {i.finish.astimezone(timezone).strftime("%d-%m-%y %H:%M %z")}'))
