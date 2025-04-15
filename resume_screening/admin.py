from django.contrib import admin

from .models import Resume, JobDescription

@admin.register(Resume)
class ResumeAdmin(admin.ModelAdmin):
    list_display = ('id', 'file', 'uploaded_at')
    search_fields = ('extracted_text',)

@admin.register(JobDescription)
class JobDescriptionAdmin(admin.ModelAdmin):
    list_display = ('id', 'raw_text', 'uploaded_at', 'resume')
    list_filter = ('resume',)
    search_fields = ('raw_text',)