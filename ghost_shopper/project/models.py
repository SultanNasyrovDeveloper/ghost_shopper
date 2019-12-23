from django.db import models
from django.shortcuts import reverse

from ghost_shopper.check.models import Check
from ghost_shopper.check.enums import CHECK_TYPES


class Project(models.Model):
    """ """
    name = models.CharField(max_length=150, verbose_name='Название проекта')
    targets = models.ManyToManyField(
        'organisation_tree.OrganisationTreeNode', blank=True, verbose_name='Цели')

    class Meta:
        verbose_name = 'Проект'
        verbose_name_plural = 'Проекты'

    def __str__(self):
        return self.name

    def get_check_template(self):
        return self.check_obj

    def multiply_checks(self):
        check = self.get_check_template()
        for target in self.targets.all():
            check.clone(target)

    def get_absolute_url(self):
        return reverse('project:detail', args=(self.id, ))
