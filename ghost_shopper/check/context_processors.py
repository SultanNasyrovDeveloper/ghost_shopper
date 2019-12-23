from . import models


def available_checks_number(request):
    number = models.Check.usual.filter(status=models.CheckStatusesEnum.AVAILABLE).count()
    return {'available_checks_number': number}
