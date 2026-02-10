from django.shortcuts import render


def module_list(request):
    return render(request, 'modules/module_list.html')


def module_detail(request, code):
    return render(request, 'modules/module_detail.html', {'code': code})
