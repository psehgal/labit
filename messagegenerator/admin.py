from django.contrib import admin
from .models import LabTest, TestRanges

# Register your models here.
admin.site.register(LabTest)
admin.site.register(TestRanges)
