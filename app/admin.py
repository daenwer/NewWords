from django.contrib import admin

from app.models.base import User
from app.models.base import Phrase, UserPhrase, UserSchedule, RepeatSchedule

# Register your models here.


# class AdminUser(admin.ModelAdmin):
#     fields = ('key', 'name', 'achievements')
#     readonly_fields = ('key',)
#     filter_horizontal = ('achievements',)


admin.site.register(User)
admin.site.register(Phrase)
admin.site.register(UserPhrase)
admin.site.register(UserSchedule)
admin.site.register(RepeatSchedule)
# admin.site.register(UserAchievementHistory, AdminUserAchievementHistory)
# admin.site.register(AchievementRequest, AdminAchievementRequest)
# admin.site.register(ApiKey, AdminApiKey)