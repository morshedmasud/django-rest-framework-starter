from django.http import HttpResponse


def index(request):
    return HttpResponse("Welcome To Django Rest API v_0.0.1")

