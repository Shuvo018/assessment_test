from django.contrib import admin
from .models import Test, Question, Option, TestAttempt, Answer

# Register your models here.

admin.site.register(Test)
admin.site.register(Question)
admin.site.register(Option)
admin.site.register(TestAttempt)
admin.site.register(Answer)






