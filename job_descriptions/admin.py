from django.contrib import admin
from .models import JobDescription, ProcessedJobDesc

admin.site.register(JobDescription)
admin.site.register(ProcessedJobDesc)

