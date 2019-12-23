import os

from django.db import models
from django.urls import reverse
from django.conf import settings
from mptt.models import MPTTModel, TreeForeignKey

from ghost_shopper.check.models import Check
from ghost_shopper.user_profile.models import User
from ghost_shopper.check.enums import CheckStatusesEnum

from .enums import DocumentGenerationTypeEnum


class OrganisationTreeNode(MPTTModel):
    """
    Organisation tree node.

    """

    name = models.CharField(max_length=150, verbose_name='Название узла')
    parent = TreeForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children')
    city = models.ForeignKey('core.City', on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Город')
    address = models.CharField(max_length=250, null=True, blank=True, verbose_name='Адрес')
    full_name = models.CharField(
        max_length=1000,
        null=True,
        blank=True,
        verbose_name='Полное имя',
        help_text='Для отчетов'
    )
    checks_theme = models.CharField(
        max_length=1000,
        null=True,
        blank=True,
        verbose_name='Тема проверок',
        help_text='Для отчетов',
    )
    contract_name = models.CharField(
        max_length=1000,
        null=True,
        blank=True,
        verbose_name='Название договора',
        help_text='Для отчетов, Например: Договор № 8/4 – КАН-АВТО от «01» марта 2016 г.'
    )
    INN = models.CharField(max_length=1000, null=True, blank=True, verbose_name='ИНН', help_text='Для отчетов')
    KPP = models.CharField(max_length=1000, null=True, blank=True, verbose_name='КПП', help_text='Для отчетов')
    legal_address = models.CharField(
        max_length=1000,
        null=True,
        blank=True,
        verbose_name='Юридический адрес',
        help_text='Для отчетов'
    )
    docs_generating_type = models.CharField(
        max_length=30,
        choices=tuple(DocumentGenerationTypeEnum.values.items()),
        default=DocumentGenerationTypeEnum.FULL,
        verbose_name='Тип генерации документов',
    )

    class Meta:
        verbose_name = 'Организации'
        verbose_name_plural = 'Организациии'

    def __str__(self):
        """
        Get string representation of class instance.
        """
        if self.type == 'organisation':
            return self.name.strip()
        elif self.type == 'location':
            return '{}({}): {}'.format(
                self.parent.name.strip() if self.parent else '',
                self.city.name if self.city else '', self.name.strip())
        elif self.type == 'department':
            return '{}: {}({})'.format(self.get_root().name.strip(), self.parent.name.strip(), self.name)

    @property
    def type(self):
        """
        Organisation node type property.
        """
        if self.level == 0:
            return 'organisation'
        elif self.level == 1:
            return 'location'
        else:
            return 'department'

    @property
    def title(self):
        """
        Organisation node title property.
        """
        return self.__str__()

    @property
    def full_title(self):
        """
        Organisation node full title property.

        Outputs current node name with name of all ancestor nodes.
        """
        return self.__str__()

    def get_descendants_ids(self):
        """
        Get ids of all descendant organisation nodes.
        """
        return tuple(self.get_descendants(include_self=True).values_list('id', flat=True))

    def get_employees(self):
        """
        Get queryset of all employees of current node and all of its descendants.
        """
        return User.objects.filter(
            is_customer=True, customer_profile__organisation_tree_node_id__in=self.get_descendants_ids()
        )

    def get_checks(self):
        """
        Get all check for this node and all descendant nodes.
        """
        descendants_ids = tuple(self.get_descendants(include_self=True).values_list('id', flat=True))
        checks = Check.objects.filter(target_id__in=descendants_ids, status=CheckStatusesEnum.CLOSED)
        return checks

    def get_current_checks(self):
        """
        Get checks list for organisation current checks list view.
        """
        descendants_ids = list(self.get_descendants(include_self=True).values_list('id', flat=True))
        if self.level == 0:
            exclude_statuses = (CheckStatusesEnum.AVAILABLE, CheckStatusesEnum.CLOSED, CheckStatusesEnum.CREATED)
            checks = Check.objects.filter(target_id__in=descendants_ids).exclude(status__in=exclude_statuses)
        else:
            checks = Check.objects.filter(target_id__in=descendants_ids, status=CheckStatusesEnum.CONFORMATION)
        return checks

    def get_chat(self):
        """
        Get organisation chat instance.
        """
        return self.get_root().chat

    def get_absolute_url(self):
        """
        Get absolute url to current organisation node.
        """
        return reverse('organisation:detail', args=(self.id, ))

    def get_address(self):
        address = ''
        if self.level == 1:
            address += self.address
        elif self.level == 2:
            address += self.parent.address
        return address


class OrganisationMonthlyDocumentStorage(models.Model):
    """
    Storage for organisation monthly documents.

    """
    organisation = models.ForeignKey(OrganisationTreeNode, on_delete=models.CASCADE, related_name='docs_storages')
    date = models.DateField()

    class Meta:
        unique_together = ('organisation', 'date')
        ordering = ('date', )

    def __str__(self):
        """Documents instance string representation."""
        return 'Хранилище документов за {}'.format(self.date.strftime('%B, %Y'))

    def save(self, *args, **kwargs):
        """
        Documents' save method.

        By convention document date should be dated first day of the month. This is used to make checks for uniqueness
        """
        if self.organisation.level != 0:
            self.organisation = self.organisation.get_root()

        if self.date.day != 1:
            self.date.replace(day=1)

        super().save(*args, **kwargs)

    def get_absolute_url(self):
        """Retrieve absolute url to the document instance."""
        return reverse('organisation:docs-detail', args=(self.id, ))


class OrganisationDocumentsContainer(models.Model):
    """
    Organisation documents instance.

    Contains one agreement and one payment document.
    """
    storage = models.ForeignKey(OrganisationMonthlyDocumentStorage, on_delete=models.CASCADE, related_name='documents')
    organisation_node = models.ForeignKey(OrganisationTreeNode, on_delete=models.CASCADE)
    agreement = models.FilePathField(
        path=os.path.join(settings.MEDIA_ROOT, 'docs/'), max_length=250, null=True, blank=True)
    payment = models.FilePathField(
        path=os.path.join(settings.MEDIA_ROOT, 'docs/'), max_length=250, null=True, blank=True)

    class Meta:
        unique_together = ('storage', 'organisation_node')





