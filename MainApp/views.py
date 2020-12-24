from json import load, dumps
# from datetime import datetime, timezone
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import *  # Check for possible namespace clashes
from .forms import Workplace_ScheduleForm, Meeting_Room_ScheduleForm
from django.http import JsonResponse
from django.utils.timezone import activate
import pytz
# from filler import check_place_schedule



@login_required()
def index(request):
    # return HttpResponse("test")
    return render(request, 'MainApp/index.html')


@login_required()
def change_room(request, show):
    if show == 'workplaces':
        workplaces = Workplace.objects.all()
        return render(request, 'MainApp/change_room.html', {'workplaces': workplaces})
    elif show == 'rooms':
        rooms = Meeting_Room.objects.all()
        return render(request, 'MainApp/change_room.html', {'rooms': rooms})


@login_required()
def my_booking(request):
    if request.is_ajax and request.method == "POST":
        place_id = request.POST.get('place_id', '')
        place_type = request.POST.get('place_type', '')
        try:
            if place_type == 'Room':
                Meeting_Room_Schedule.objects.get(pk=int(place_id)).delete()
                # return JsonResponse(dumps(f'Deleted successfully'), safe=False, status=200)
            elif place_type == 'Workplace':
                Workplace_Schedule.objects.get(pk=int(place_id)).delete()
            return JsonResponse(dumps(f'Deleted successfully'), safe=False, status=200)
        except Exception:
            return JsonResponse(dumps({'Deletion error': ''}), safe=False, status=400)

    workplaces = Workplace_Schedule.objects.filter(
        user_id=request.user.id).order_by('start')
    rooms = Meeting_Room_Schedule.objects.filter(
        user_id=request.user.id).order_by('start')
    user_tz = request.user.user_preferences.timezone.split(',')[0].strip()
    activate(pytz.timezone(user_tz))
    return render(request, 'MainApp/my_booking.html', {'rooms': rooms, 'workplaces': workplaces, 'user_tz': user_tz})


# @login_required()
# def book(request):
#     if request.is_ajax and request.method == "POST":
#         # get the form data
#         date = request.POST.get('date', '')
#         start = request.POST.get('start', '')
#         finish = request.POST.get('finish', '')
#         place_id = request.POST.get('place_id', '')
#         place_type = request.POST.get('place_type', '')

#         if not all([date, start, finish, place_id, place_type]):
#             return JsonResponse({"error": "400"}, status=400)

#         dt_start = datetime.strptime(date + ' ' + start, '%d/%m/%y %H:%M')
#         dt_finish = datetime.strptime(date + ' ' + finish, '%d/%m/%y %H:%M')
#         # ******************
#         print(start)
#         event_date=datetime.strptime(date,"%Y%m%d")
#         event_start=datetime.strptime(start,"%H%M%S")
#         event_finish=datetime.strptime(finish,"%H%M%S")
#         # ******************
#         # str_utcoffset = 'UTC' + start.split(' ')[-1]
#         try:
#             str_utcoffset = request.user.user_preferences.timezone.split(
#                 ',')[-1].strip()
#         except Exception:
#             return JsonResponse(dumps({'error': 'User has no timezone'}), safe=False, status=400)

#         res, cause = check_place_schedule(
#             place_id, str_utcoffset, dt_start, dt_finish, place_type)
#         if not res:
#             return JsonResponse({'error': cause}, safe=False, status=400)

#         if place_type == 'Workplace':
#             Workplace_Schedule.objects.create(workplace_id=place_id, user_id=request.user.id,
#                                               start=dt_start.astimezone(
#                                                   timezone.utc),
#                                               finish=dt_finish.astimezone(timezone.utc))
#             response = {'start': start, 'finish': finish,
#                         'date': date, 'timezone': str_utcoffset}
#             send_event(event_date,'Workplace',event_start,event_finish,'test4864@yandex.ru','sihcmwvranazjwxo')
#             return JsonResponse(dumps(response), safe=False, status=200)

#         elif place_type == 'Room':
#             Meeting_Room_Schedule.objects.create(meeting_room_id=place_id, user_id=request.user.id,
#                                                  start=dt_start.astimezone(
#                                                      timezone.utc),
#                                                  finish=dt_finish.astimezone(timezone.utc))
#             response = {'start': start, 'finish': finish,
#                         'date': date, 'timezone': str_utcoffset}
#             send_event(date, 'Room', start, finish, 'test4864@yandex.ru', 'sihcmwvranazjwxo')
#             return JsonResponse(dumps(response), safe=False, status=200)

#     # some error occured
#     return JsonResponse({"error": "unknown error"}, status=400)
