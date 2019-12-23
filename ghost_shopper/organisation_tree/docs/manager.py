from dateutil.relativedelta import relativedelta

from ghost_shopper.organisation_tree.models import OrganisationMonthlyDocumentStorage, OrganisationDocumentsContainer
from ghost_shopper.organisation_tree.enums import DocumentGenerationTypeEnum

from .agreement import AgreementDocument
from .payment import PaymentDocument


class OrganisationsDocumentManager(object):
    """
    Monthly organisation documents manager.

    Manager is responsible for creating documents for every organisation that had at least 1 check performed past month.

    """

    def __init__(self, date, organisation):
        """
        Initialize class.
        """

        self.date = date.replace(day=1)
        if not organisation.level == 0:
            organisation = organisation.get_root()
        self.organisation = organisation

    def make_documents(self):
        """
        Make monthly documents fo given organisation.

        Makes monthly documents. Documents could be generated for whole organisation or for every organisation location.

        """
        storage, _ = OrganisationMonthlyDocumentStorage.objects.get_or_create(
            organisation=self.organisation, date=self.date
        )

        if self.organisation.docs_generating_type == DocumentGenerationTypeEnum.FULL:
            container = self._create_docs_container(self.organisation, storage)
            self._generate_docs(container, self.organisation)

        else:
            for node in self.organisation.get_children():
                container = self._create_docs_container(node, storage)
                self._generate_docs(container, node)

    def _create_docs_container(self, organisation, storage):
        """
        Create organisation documents storage instance.
        """
        container, _ = OrganisationDocumentsContainer.objects.get_or_create(
            organisation_node=organisation,
            storage=storage,
        )
        return container

    def _generate_docs(self, container, organisation):
        """
        Generate docs for given organisation node.
        """
        checks = self._get_monthly_checks(organisation)

        doc = AgreementDocument(id=container.id, organisation=organisation, date=self.date, checks=checks)
        doc.generate()
        container.agreement = doc.path_to_file

        doc = PaymentDocument(id=container.id, organisation=organisation, date=self.date, checks=checks)
        doc.create()
        container.payment = doc.path_to_file

        container.save()

    def _get_monthly_checks(self, organisation):
        """
        Organisation closed organisation checks for month in the date.
        """
        start_date = self.date
        end_date = start_date + relativedelta(months=+1, days=-1)
        checks = organisation.get_checks().filter(
            checklist__visit_date__gte=start_date, checklist__visit_date__lte=end_date,
        )
        return checks
