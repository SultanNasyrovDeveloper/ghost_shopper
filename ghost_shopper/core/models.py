""" Technically its not a core module. Here i put all entities that a don't understand where to put them.
    Kind a entities trash.
"""
from django.db import models


class CheckKind(models.Model):
    """Check kind."""
    name = models.CharField(max_length=1000, verbose_name='Название')
    price = models.SmallIntegerField(default=0, verbose_name='Цена')

    def __str__(self):
        return self.name


class MyOrganisation(models.Model):
    """Data about organisation that is necessary for some documents."""
    full_name = models.CharField(max_length=1000, null=True, blank=True, verbose_name='Полное название')
    short_name = models.CharField(max_length=500, null=True, blank=True, verbose_name='Сокращенное название')
    INN = models.CharField(max_length=50, null=True, blank=True, verbose_name='ИНН')
    KPP = models.CharField(max_length=50, null=True, blank=True, verbose_name='КПП')
    account = models.CharField(max_length=50, null=True, blank=True, verbose_name='Расчетный счет')
    address = models.CharField(max_length=1000, null=True, blank=True, verbose_name='Юридический адрес')
    phone_number = models.CharField(max_length=50, null=True, blank=True, verbose_name='Номер телефона')

    bank_name = models.CharField(max_length=1000, null=True, blank=True, verbose_name='Название банка')
    bank_BIC = models.CharField(max_length=25, null=True, blank=True, verbose_name='БИК банка')
    bank_account = models.CharField(max_length=50, null=True, blank=True, verbose_name='Расчетный счет банка')

    @classmethod
    def get(cls):
        instance, _ = cls.objects.get_or_create(id=1)
        return instance


class City(models.Model):
    """  """
    name = models.CharField(max_length=70, verbose_name='Название')

    class Meta:
        verbose_name = 'Город'
        verbose_name_plural = 'Города'

    def __str__(self):
        return self.name


class CarBrand(models.Model):
    """ Car brand system model """
    name = models.CharField(max_length=50, verbose_name='Название')

    def __str__(self):
        return self.name


class CarModel(models.Model):
    """ Car model system model """
    brand = models.ForeignKey(CarBrand, on_delete=models.CASCADE, related_name='models', verbose_name='Марка')
    name = models.CharField(max_length=100, verbose_name='Название')

    def __str__(self):
        return self.name


class PerformerLettersTemplates(models.Model):
    """ Model for storing check perform invitation letter body text """

    default_invite = 'Уважаемый, {performer}! \nПредлагаем Вам провести {check}.\n{link}'

    default_apply = 'Уважаемый, {performer}! \nВас одобрили для проведения проверки {check}.\n{link}'

    invite_subject = 'Приглашаем Вас провести проверку'
    invite_message = models.TextField(default=default_invite)

    apply_subject = 'Ваша заявка на проведение проверки одобрена'
    apply_message = models.TextField(default=default_apply)

    @classmethod
    def get(cls):
        instance, _ = cls.objects.get_or_create(id=1)
        return instance



