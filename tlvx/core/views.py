from django.http import HttpResponse
from django.shortcuts import redirect
from django.template import RequestContext, loader


def main(request, name):
    template = loader.get_template('angular/%s.html' % name)
    context = RequestContext(request, {})
    return template.render(context)


def index(request, path=None):
    return HttpResponse(main(request, 'index'))
