from celery import shared_task


@shared_task
def create_documents():
    from datetime import date
    from dateutil.relativedelta import relativedelta
    from ghost_shopper.organisation_tree.models import OrganisationTreeNode
    from ghost_shopper.check.models import Check
    from ghost_shopper.organisation_tree.docs.manager import OrganisationDocumentsManager
    # get all previous month date
    today = date.today()
    today = today.replace(day=1)
    previous_month_first_day = today + relativedelta(months=-1)
    previous_month_last_day = today + relativedelta(days=-1)

    # get all organisation that had checks prev month
    organisation_ids = set(
        Check.objects.filter(
            checklist__visit_date__lte=previous_month_last_day,
            checklist__visit_date__gte=previous_month_first_day
        ).values_list('target_id', flat=True)
    )
    organisations = OrganisationTreeNode.objects.filter(id__in=organisation_ids)
    # start doc creator on them
    for organisation in organisations:
        manager = OrganisationDocumentsManager(organisation=organisation, date=previous_month_first_day)
        manager.generate()
