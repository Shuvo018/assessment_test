from django.contrib import admin
from .models import Test, Question, QuestionImage, Option, TestAttempt, Answer


class TestAdmin(admin.ModelAdmin):
    list_display = ("title", "teacher", "status", "shared_code", "created_at")
    readonly_fields = ("shared_code", "created_at", "updated_at")
    list_filter = ("status", "teacher")
    search_fields = ("title", "description", "shared_code")


admin.site.register(Test, TestAdmin)
admin.site.register(Question)
admin.site.register(QuestionImage)
admin.site.register(Option)
admin.site.register(TestAttempt)
admin.site.register(Answer)






