from typing import Dict



class ChecksStatistics:
    """
    Calculate statistical data for given checks queryset.
    """
    def __init__(self, checks):
        """
        Initialize class.
        """

        self.checks = checks
        self.checks_number = checks.count()
        self._overall = {
            'points_total': 0,
            'points': 0,
            'percentage': None,
        }
        self._sections = {}

    @property
    def overall(self):
        """
        Get overall statistics data
        """
        return self._overall

    @property
    def sections(self):
        """
        Get section by statistical data
        """
        return self._sections

    def calculate(self):
        """
        Calculates statistics according to given queryset.
        """
        checks_statistics = [check.checklist.get_statistics() for check in self.checks]
        for check_data in checks_statistics:
            self._add_check_data(check_data)
        self._overall['percentage'] = self._calculate_percentage(self._overall['points_total'], self._overall['points'])

    def _add_check_data(self, check_data: Dict) -> None:
        """
        Add new check data to statistics and recalculate overall statistics.
        """
        self._overall['points_total'] += check_data.get('points_total', 0)
        self._overall['points'] += check_data.get('points', 0)
        for section_name, section_data in check_data['sections'].items():
            self._add_section_data(section_name, section_data)

    def _add_section_data(self, section_name, section_data):
        """
        Add section data to sections dict and calculate percentage.
        """
        if not section_name in self._sections:
            self._sections[section_name] = {'points_total': 0, 'points': 0, 'percentage': 0, 'subsections': dict()}

        section = self._sections[section_name]
        section['points_total'] += section_data['points_total']
        section['points'] += section_data['points']

        for subsection_name, subsection_data in section_data['subsections']:
            self._add_subsection(subsection_name, subsection_data, section)

        section['percentage'] = self._calculate_percentage(section['points_total'], section['points'])

    def _add_subsection(self, subsection_name, subsection_data, parent_section):
        """
        Add subsection data to the section.
        """
        if not subsection_name in parent_section['subsections']:
            parent_section['subsections'][subsection_name] = {'points_total': 0, 'points': 0, 'percentage': 0}

        subsection = parent_section['subsections'][subsection_name]
        subsection['points_total'] += subsection_data['points_total']
        subsection['points'] += subsection_data['points']

        subsection['percentage'] = self._calculate_percentage(subsection['points_total'], subsection['points'])

    def _calculate_percentage(self, points_total, points):
        """
        Calculate percentage.
        """
        if not points_total or not points:
            return 0
        return round(points / (points_total / 100))


class ChecksStatisticsByOrganisation(object):
    """
    Aggregates check statistics by different targets.

    """

    def __init__(self, checks) -> None:
        """
        Initialize class.

        Args:
            checks (QuerySet): queryset of checks for one organisation.
        """
        self.checks = checks
        self.calculator = ChecksStatistics
        self.data = {}

    def calculate(self) -> dict:
        """
        Calculate metrics for every organisation node that is in given checks queryset.
        """
        self.data = {}

        # calculate overall statistics
        statistics = ChecksStatistics(checks=self.checks)
        statistics.calculate()
        overall_data = statistics.overall
        overall_data['sections'] = statistics.sections
        self.data['overall'] = overall_data

        # calculate statistics for every target node
        self.data['nodes'] = {}
        sections = self.data['nodes']
        targets = list(set(
            (check.target_id, check.target.full_title ) for check in self.checks
        ))

        for target_id, target_name in targets:
            statistics = self.calculator(self.checks.filter(target_id=target_id))
            statistics.calculate()
            overall_target_data = statistics.overall
            overall_target_data['sections'] = statistics.sections
            sections[target_name] = overall_target_data

        return self.data
