import json


def icons(request):
    from tlvx.core.models import MarkerIcon
    icons = [m.data(request) for m in MarkerIcon.objects.all()]
    return {'icons': json.dumps({'data': icons})}
