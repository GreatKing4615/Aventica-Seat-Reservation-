from django.contrib import admin
from .models import *


# # class CommentInline(admin.TabularInline):
# #     model = Comment
# #     extra = 0


@admin.register(User_preferences)
class User_preferencesAdmin(admin.ModelAdmin):
    fields = (())
#     # inlines = [CommentInline, ]
#     # list_display = ('poll_text', 'pub_date', 'pub_by')
#     # ordering = ('pub_date',)
#     # list_filter = ('pub_date',)
#     # search_fields = ('pub_date', 'poll_text', 'pub_by')
#     #     fieldsets = (('Required Information', {'description': "Required for each poll",
#     #                                            'fields': ('poll_text', 'pub_date',)}),
#     #                  ('Additional information', {'classes': ('collapse',),
#     #                                              'fields': ('pub_by', 'votes')}),)
#     # # admin.site.register(poll)


@admin.register(Meeting_Room)
class Meeting_RoomAdmin(admin.ModelAdmin):
    fields = (())


@admin.register(Workplace)
class WorkplaceAdmin(admin.ModelAdmin):
    fields = (())


@admin.register(Workplace_Schedule)
class Workplace_ScheduleAdmin(admin.ModelAdmin):
    fields = (())


@admin.register(Meeting_Room_Schedule)
class Meeting_Room_ScheduleAdmin(admin.ModelAdmin):
    fields = (())
