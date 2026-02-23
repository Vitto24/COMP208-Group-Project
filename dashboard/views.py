from django.shortcuts import render
from modules.models import Module
from grades.models import Assignment
from django.utils import timezone
from datetime import timedelta

def dashboard(request):
    
    modules = Module.objects.all()
    
    now = timezone.now()
    three_days_from_now = now + timedelta(days=3)
    
    #Calculates the which is due soon with 3 being the threshodl.
    assignments = Assignment.objects.filter(due_date__gte=now).order_by('due_date')
    return render(request, 'dashboard/dashboard.html', {
        'modules': modules,
        'assignments': assignments,
        'three_days_from_now': three_days_from_now,
        'now': now,
    })
