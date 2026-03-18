from django.shortcuts import render

def get_info(request):
    return render(request, 'info.html')

def hello(request):
    return render(request, 'hello.html')


# Create your views here.
