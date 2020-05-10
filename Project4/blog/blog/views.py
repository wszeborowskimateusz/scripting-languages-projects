from django.http import HttpResponse
from django.shortcuts import render

def handler404(request, exception):
    print("I AM IN")
    response = render(request, '404.html')
    return response