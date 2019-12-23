from . import models
from .enums import ApprovalRequestStatusesEnum


def approval_requests_number(request):
    number = models.PerformerApproveRequest.objects.filter(status=ApprovalRequestStatusesEnum.ACTIVE).count()
    return {'approval_requests_number': number}

