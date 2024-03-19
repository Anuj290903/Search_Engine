from django.contrib import admin
from .models import MyUser, MyExperience, MyEducation

# Register your models here.

admin.site.register(MyUser)
admin.site.register(MyExperience)
admin.site.register(MyEducation)