from json import dumps
from django.shortcuts import render
from django.http import HttpResponseRedirect, JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
# from django.contrib import messages
# from django.urls import reverse
from MainApp.models import Workplace_Schedule, Meeting_Room_Schedule, User, User_preferences, Meeting_Room, Workplace
from datetime import datetime, timezone, timedelta
from filler import check_place_schedule, place_shedule_strings, place_strings
from yandex_cal import send_event
from social_django.models import UserSocialAuth


@login_required()
def settings(request):
    return render(request, 'settings.html')


@login_required()
def profile(request):
    if request.is_ajax and request.method == "POST" and request.POST.get('ntz', ''):
        timezones = [
            'Europe/Kaliningrad, UTC+02:00',
            'Europe/Moscow, UTC+03:00',
            'Europe/Volgograd, UTC+04:00',
            'Asia/Yekaterinburg, UTC+05:0s0',
            'Asia/Omsk, UTC+06:00',
            'Asia/Krasnoyarsk, UTC+07:00',
            'Asia/Irkutsk, UTC+08:00',
            'Asia/Yakutsk, UTC+09:00',
            'Asia/Vladivostok, UTC+10:00',
            'Asia/Sakhalin, UTC+11:00',
            'Asia/Kamchatka, UTC+12:00'
        ]
        new_timezone = request.POST.get('ntz', '')
        if new_timezone not in timezones:
            return JsonResponse({"error": "Invalid timezone"}, status=400)
        ups = request.user.user_preferences
        ups.timezone = new_timezone
        ups.save()
        return JsonResponse(dumps(f'timezone changed to {new_timezone}'), safe=False, status=200)
    
    if request.is_ajax and request.method == "POST" and request.POST.get('app_pass', ''):
        app_pass = request.POST.get('app_pass', '')
        ups = request.user.user_preferences
        ups.app_password = app_pass
        ups.save()
        return JsonResponse(dumps(f'app password changed to {app_pass}'), safe=False, status=200)

    try:
        timezone = request.user.user_preferences.timezone
        app_password = request.user.user_preferences.app_password
    except Exception:
        ups = User_preferences.objects.create(
            user=request.user, timezone='Asia/Yekaterinburg, UTC+05:00')
        timezone = ups.timezone
        app_password = ''
    return render(request, "profile.html", {"timezone": timezone, "app_password": app_password})


@login_required()
def notifications_settings(request):
    return render(request, 'notifications_settings.html')


@login_required()
def sign_in(request):
    return render(request, 'sign_in.html')


@login_required()
def sign_up(request):
    return render(request, 'sign_up.html')


def check_schedule(request):
    if request.method == 'GET':
        date = request.GET.get('date', '')
        start = request.GET.get('start', '')
        finish = request.GET.get('finish', '')
        place_id = request.GET.get('place_id', '')
        place_type = request.GET.get('place_type', '')
        username = request.GET.get('username', request.user.username)
        repeat = request.GET.get('repeat', '')
        # include_holydays = request.GET.get('include_holydays', '') later

        if not all([date, start, finish, place_id, place_type, username, repeat]):
            return JsonResponse(dumps({"Some data is missing":
                                       [date, start, finish, place_id, place_type, username, repeat]}), safe=False, status=400)

        user = User.objects.filter(username=username)[0]
        dates = []
        if repeat == 'current_week' or repeat == 'next_and_current_week':
            dates = [(datetime.strptime(date, '%d/%m/%y').date() + timedelta(days=x)).strftime('%d/%m/%y')
                     for x in range(5 - datetime.strptime(date, '%d/%m/%y').weekday())]
        if repeat == 'next_and_current_week':
            dates.extend(
                [(datetime.strptime(dates[-1], '%d/%m/%y') + timedelta(days=x)).strftime('%d/%m/%y') for x in range(3, 8)])
        if repeat == 'once':
            dates = [date]
        str_utcoffset = user.user_preferences.timezone.split(',')[-1].strip()
        # user_tz = user.user_preferences.timezone.split(',')[0].strip()

        responses = {}
        fails = 0
        for date in dates:
            dt_start = datetime.strptime(date + ' ' + start, '%d/%m/%y %H:%M')
            dt_finish = datetime.strptime(
                date + ' ' + finish, '%d/%m/%y %H:%M')
            res, cause = check_place_schedule(
                place_id, str_utcoffset, dt_start, dt_finish, place_type)
            responses[date] = f'{cause}'
            if not res:
                fails += 1
        
        if len(responses) == fails:
            return JsonResponse(dumps({'fail': 'All booked'}), safe=False, status=200)

        return JsonResponse(dumps(responses), safe=False, status=200)


def book(request):
    if request.is_ajax and request.method == "POST":
        # get the form data
        date = request.POST.get('date', '')
        start = request.POST.get('start', '')
        finish = request.POST.get('finish', '')
        place_id = request.POST.get('place_id', '')
        place_type = request.POST.get('place_type', '')
        username = request.POST.get('username', request.user.username)
        repeat = request.POST.get('repeat', '')

        if not all([date, start, finish, place_id, place_type, username, repeat]):
            return JsonResponse(dumps({"Some data is missing":
                                       [date, start, finish, place_id, place_type, username, repeat]}), safe=False, status=400)

        user = User.objects.filter(username=username)[0]
        try:
            str_utcoffset = user.user_preferences.timezone.split(
                ',')[-1].strip()
        except Exception:
            return JsonResponse(dumps({'error': 'User has no timezone'}), safe=False, status=400)

        dates = []
        if repeat == 'current_week' or repeat == 'next_and_current_week':
            dates = [(datetime.strptime(date, '%d/%m/%y').date() + timedelta(days=x)).strftime('%d/%m/%y')
                     for x in range(5 - datetime.strptime(date, '%d/%m/%y').weekday())]
        if repeat == 'next_and_current_week':
            dates.extend(
                [(datetime.strptime(dates[-1], '%d/%m/%y') + timedelta(days=x)).strftime('%d/%m/%y') for x in range(3, 8)])
        if repeat == 'once':
            dates = [date]

        responses = {}
        for date in dates:
            dt_start = datetime.strptime(date + ' ' + start, '%d/%m/%y %H:%M')
            dt_finish = datetime.strptime(date + ' ' + finish, '%d/%m/%y %H:%M')

            res, cause = check_place_schedule(
                place_id, str_utcoffset, dt_start, dt_finish, place_type)
            responses[date] = {'fail': cause}
            if res:
                if place_type == 'Workplace':
                    Workplace_Schedule.objects.create(workplace_id=place_id, user_id=user.id, start=dt_start.astimezone(
                        timezone.utc), finish=dt_finish.astimezone(timezone.utc))
                    responses[date] = {'from': dt_start.strftime("%H:%M"), 'to': dt_finish.strftime("%H:%M")}
                    send_event(f'Workplace #{place_id}', dt_start, dt_finish, user.email, user.user_preferences.app_password)

                elif place_type == 'Room':
                    Meeting_Room_Schedule.objects.create(meeting_room_id=place_id, user_id=user.id, start=dt_start.astimezone(
                        timezone.utc), finish=dt_finish.astimezone(timezone.utc))
                    responses[date] = {'from': dt_start.strftime("%H:%M"), 'to': dt_finish.strftime("%H:%M")}
                    send_event(f'Room #{place_id}', dt_start, dt_finish, user.email, user.user_preferences.app_password)
        
        return JsonResponse(dumps(responses), safe=False, status=200)

    # some error occured
    return JsonResponse({"error": "unknown error"}, status=400)


@csrf_exempt
def telega_book(request):
    if request.method == "POST":
        # get the request data
        date = request.POST.get('date', '')
        start = request.POST.get('start', '')
        finish = request.POST.get('finish', '')
        place_id = request.POST.get('place_id', '')
        place_type = request.POST.get('place_type', '')
        username = request.POST.get('username', '')

        if not all([date, start, finish, place_id, place_type, username]):
            # return JsonResponse(dumps([x for x in request.POST.items()]), safe=False, status=400)
            return JsonResponse(dumps({"Some data is missing": [date, start, finish, place_id, place_type, username]}),
                                safe=False, status=400)

        dt_start = datetime.strptime(date + ' ' + start, '%d/%m/%y %H:%M')
        dt_finish = datetime.strptime(date + ' ' + finish, '%d/%m/%y %H:%M')
        # str_utcoffset = 'UTC' + start.split(' ')[-1]
        user = User.objects.filter(username=username)[0]
        str_utcoffset = user.user_preferences.timezone.split(',')[-1].strip()
        user_tz = user.user_preferences.timezone.split(',')[0].strip()

        res, cause = check_place_schedule(
            place_id, str_utcoffset, dt_start, dt_finish, place_type)
        if not res:
            return JsonResponse(dumps({"error": cause}), safe=False, status=400)

        if place_type == 'Workplace':
            Workplace_Schedule.objects.create(workplace_id=place_id, user_id=user.id,
                                              start=dt_start.astimezone(
                                                  timezone.utc),
                                              finish=dt_finish.astimezone(timezone.utc))
            # response = {'start': start, 'finish': finish, 'date': date}
            response = f'booked on {date} from {start} to {finish}, {user_tz}'
            return JsonResponse(dumps(response), safe=False, status=200)

        elif place_type == 'Room':
            Meeting_Room_Schedule.objects.create(meeting_room_id=place_id, user_id=user.id,
                                                 start=dt_start.astimezone(
                                                     timezone.utc),
                                                 finish=dt_finish.astimezone(timezone.utc))
            # response = {'start': start, 'finish': finish, 'date': date}
            response = f'booked on {date} from {start} to {finish}, {user_tz}'
            return JsonResponse(dumps(response), safe=False, status=200)

    # some error occured
    return JsonResponse(dumps({"error": 'unknown error'}), safe=False, status=400)


def telega_auth(request):
    if request.method == "GET":
        username = request.GET.get('username', '')
        users = User.objects.all()
        for user in users:
            print(user)
            if str(username) == str(user):
                return JsonResponse(dumps({'username': user.id}), safe=False, status=200)
        return JsonResponse(dumps({'error': 'Invalid username'}), safe=False, status=400)
    return JsonResponse(dumps({'error': 'bad request'}), safe=False, status=400)


def telega_fetch_rooms(request):
    if request.method == "GET":
        place_type = request.GET.get('place_type', '')

        if place_type == 'Room':
            mrs = Meeting_Room.objects.all()
            print('***')
            print(mrs)
            print('***')

            response = place_strings(mrs, 'Meeting Room')
            return JsonResponse(dumps(response), safe=False, status=200)

        elif place_type == 'Workplace':
            wps = Workplace.objects.all()
            response = place_strings(wps, 'Workplace')
            return JsonResponse(dumps(response), safe=False, status=200)

        return JsonResponse(dumps({'error': 'Invalid place_type'}), safe=False)
        # if not all([date, start, finish, place_id, place_type, username]):
    return JsonResponse(dumps({'error': 'bad request'}), safe=False, status=400)


def telega_fetch(request):
    if request.method == "GET":
        place_id = request.GET.get('place_id', '')
        place_type = request.GET.get('place_type', '')
        date = request.GET.get('date', '')
        username = request.GET.get('username', '')

        if place_type:
            if place_type == 'Room':
                mrs = Meeting_Room_Schedule.objects.all().order_by('start')
                if date:
                    mrs = mrs.filter(start__date=datetime.strptime(
                        date, '%d/%m/%y').date())
                if place_id:
                    mrs = mrs.filter(room_id=place_id)
                if username:
                    mrs = mrs.filter(user__username=username)
                response = place_shedule_strings(mrs, 'Meeting Room')
                return JsonResponse(dumps(response), safe=False, status=200)

            elif place_type == 'Workplace':
                wps = Workplace_Schedule.objects.all().order_by('start')
                if date:
                    wps = wps.filter(start__date=datetime.strptime(
                        date, '%d/%m/%y').date())
                if place_id:
                    wps = wps.filter(workplace_id=place_id)
                if username:
                    wps = wps.filter(user__username=username)
                response = place_shedule_strings(wps, 'Workplace')
                return JsonResponse(dumps(response), safe=False, status=200)

            return JsonResponse(dumps({'error': 'Invalid place_type'}), safe=False)
        # if not all([date, start, finish, place_id, place_type, username]):
        return JsonResponse(dumps({"Some data is missing": [date, place_id, place_type, username]}), safe=False,
                            status=400)
