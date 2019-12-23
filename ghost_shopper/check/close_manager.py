from datetime import date

from dateutil.relativedelta import relativedelta

from .enums import CheckStatusesEnum
from .models import Check


class CheckCloseManger(object):
    """Closes all check that has expired appeal period or expired appeal answer period."""

    def perform(self):
        """Close all checks with expired date"""
        today = date.today()

        checks = Check.usual.filter(status=CheckStatusesEnum.CONFORMATION)

        for check in checks:
            if check.sent_for_conformation_date is None:
                check.sent_for_conformation_date = today
                continue

            conformation_period_expires_date = check.sent_for_conformation_date + relativedelta(
                days=+check.conformation_period)
            if conformation_period_expires_date <= today:
                check.close()
