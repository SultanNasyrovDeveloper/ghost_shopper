import os

from dateutil.relativedelta import relativedelta
from django.conf import settings
from pathlib import Path

from ghost_shopper.core.models import MyOrganisation


class BaseDocument:

    my_organisation = MyOrganisation.get()

    @property
    def file_name(self):
        return NotImplementedError

    @property
    def path_to_file(self):
        """
        Get absolute path to the file.

        Get path files directory if not exist create one.
        """
        target_folder_path = os.path.join(settings.MEDIA_ROOT, 'docs/')
        target_folder = Path(target_folder_path)
        if not target_folder.exists():
            os.mkdir(target_folder_path)
        return os.path.join(target_folder, self.file_name)

    def _get_months_last_day(self):
        """Get last day of the month"""
        month_first_day = self.date.replace(day=1)
        next_month_fist_day = month_first_day + relativedelta(months=+1)
        month_last_day = next_month_fist_day + relativedelta(days=-1)
        return month_last_day.day
