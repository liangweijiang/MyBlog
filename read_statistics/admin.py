from django.contrib import admin
from .models import ReadNum


# Register your models here.

@admin.register(ReadNum)
class ReadAdmin(admin.ModelAdmin):
    list_dispaly = ('read_num', 'content_object')
