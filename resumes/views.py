from django.shortcuts import render
from .forms import ResumeUploadForm

def upload_resume(request):
    if request.method == 'POST':
        form = ResumeUploadForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
    else:
        form = ResumeUploadForm()
    return render(request, 'upload.html', {'form': form})

