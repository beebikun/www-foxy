from django.http import HttpResponse
from django.shortcuts import redirect

from .models import RegistrationProfile


def static(request, path=None):
	if path: path = '/static/' + path
    return redirect(path)