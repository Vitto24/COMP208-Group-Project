from django.shortcuts import render

TIME_SLOTS = [
    '09:00', '10:00', '11:00', '12:00',
    '13:00', '14:00', '15:00', '16:00', '17:00',
]

DAYS = ['MON', 'TUE', 'WED', 'THU', 'FRI']


def timetable_view(request):
    # TODO: Query TimetableEntry.objects.filter(student=request.user)
    # and organise into a grid structure for the template
    return render(request, 'timetable/timetable.html', {
        'time_slots': TIME_SLOTS,
        'days': DAYS,
        'entries': [],  # TODO: replace with real query
    })
