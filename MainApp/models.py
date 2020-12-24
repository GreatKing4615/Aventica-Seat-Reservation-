from django.db import models
from django.contrib.auth.models import User


class User_preferences(models.Model):
    ru_timezones = [
        (2, 'Europe/Kaliningrad, UTC+02:00'),
        (3, 'Europe/Moscow, UTC+03:00'),
        (4, 'Europe/Volgograd, UTC+04:00'),
        (5, 'Asia/Yekaterinburg, UTC+05:00'),
        (6, 'Asia/Omsk, UTC+06:00'),
        (7, 'Asia/Krasnoyarsk, UTC+07:00'),
        (8, 'Asia/Irkutsk, UTC+08:00'),
        (9, 'Asia/Yakutsk, UTC+09:00'),
        (10, 'Asia/Vladivostok, UTC+10:00'),
        (11, 'Asia/Sakhalin, UTC+11:00'),
        (12, 'Asia/Kamchatka, UTC+12:00')
    ]
    user = models.OneToOneField(
        User, on_delete=models.CASCADE)
    timezone = models.CharField(choices=ru_timezones, max_length=32, default=ru_timezones[1][1])
    photo = models.ImageField(blank=True, null=True)
    yandex_mail = models.EmailField(blank=True, null=True)
    sync_on = models.BooleanField(default=False)
    notifications_on = models.BooleanField(default=False)
    app_password = models.CharField(default='', max_length=32)


class Workplace(models.Model):
    name = models.CharField(max_length=50)
    description = models.TextField(blank=True, null=True)


class Meeting_Room(models.Model):
    name = models.CharField(max_length=50)
    capacity = models.IntegerField()
    description = models.TextField(blank=True, null=True)


class Workplace_Schedule(models.Model):
    workplace = models.ForeignKey(
        Workplace, on_delete=models.CASCADE)
    user = models.ForeignKey(
        User, on_delete=models.CASCADE)
    start = models.DateTimeField()
    finish = models.DateTimeField()


class Meeting_Room_Schedule(models.Model):
    meeting_room = models.ForeignKey(
        Meeting_Room, on_delete=models.CASCADE)
    user = models.ForeignKey(
        User, on_delete=models.CASCADE)
    start = models.DateTimeField()
    finish = models.DateTimeField()
