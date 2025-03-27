from django.shortcuts import render
from .forms import JobDescUploadForm
from django.shortcuts import redirect

def upload_job_desc(request):
    if request.method == 'POST':
        form = JobDescUploadForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            #return redirect('success_page')  
    else:
        form = JobDescUploadForm()
    return render(request, 'upload.html', {'form': form})