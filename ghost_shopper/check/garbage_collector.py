from datetime import date

from dateutil.relativedelta import relativedelta

from .models import Check


class GarbageCollector:
    """ Garbage collector deletes old audio files """

    def perform(self):
        """ Get all old checks and delete their checklists audio """
        today = date.today()
        three_month_ago = today + relativedelta(months=-3)
        for check in Check.objects.filter(checklist__visit_date__lt=three_month_ago):
            check.checklist.audio = None
            check.checklist.save()
