from django.shortcuts import render


def grades(request):
    return render(request, 'grades/grades.html')
