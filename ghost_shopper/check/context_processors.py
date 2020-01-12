from . import models


def available_checks_number(request):
    number = models.Check.usual.filter(status=models.CheckStatusesEnum.AVAILABLE).count()
    return {'available_checks_number': number}


def current_checks_number(request):
    checks_number = 0
    if not request.user.is_anonymous:
        if request.user.is_performer:
            checks_number= models.Check.usual.filter(performer=request.user).exclude(
                status=models.CheckStatusesEnum.CLOSED).count()
        if request.user.is_customer:
            organisation = request.user.profile.organisation_tree_node
            checks = models.Check.usual.filter(id__in=organisation.get_descendants_ids())
            checks_number = checks.exclude(
                status__in=(
                    models.CheckStatusesEnum.CREATED,
                    models.CheckStatusesEnum.AVAILABLE,
                    models.CheckStatusesEnum.CLOSED,
                )
            ).count()
    return {'current_checks_number': checks_number}
