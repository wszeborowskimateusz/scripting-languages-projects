from django.http import HttpResponse
from django.shortcuts import render

def handler404(request, exception):
    response = render(request, '404.html')
    return response