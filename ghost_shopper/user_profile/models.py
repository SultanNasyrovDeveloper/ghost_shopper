from datetime import date
from dateutil.relativedelta import relativedelta

from django.db import models
from django.contrib.auth.models import PermissionsMixin, AbstractUser
from django.contrib.auth.base_user import AbstractBaseUser
from django.core.exceptions import ValidationError
from django.urls import reverse

from .enums import ApprovalRequestStatusesEnum


class User(AbstractUser):
    """ User model used in the system
        Specified additional user fields
        User can be performer, customer and staff
        Args:
            avatar (FileField): user image
            username (CharField): default field
            first_name (CharField): default field
            last_name (CharField): default
            patronymic (CharField): custom field holds patronymic
            email (EmailField): default
            is_performer (BooleanField): True if user is performer
            is_customer (BooleanField): True if user is customer

    """
    avatar = models.FileField(upload_to='user_avatars/', blank=True, null=True, verbose_name='Аватар')
    first_name = models.CharField(max_length=30, null=True, blank=True, verbose_name='Имя')
    last_name = models.CharField(max_length=150, null=True, blank=True, verbose_name='Фамилия')
    patronymic = models.CharField(max_length=70, null=True, blank=True, verbose_name='Отчество')
    phone_number = models.CharField(max_length=30, null=True, blank=True, verbose_name='Контактный номер')

    is_customer = models.BooleanField(default=False, verbose_name='Является заказчиком')
    is_performer = models.BooleanField(default=False, verbose_name='Является тайным покупателем')

    @property
    def status(self):
        if self.is_customer:
            return 'Заказчик'
        elif self.is_performer:
            return 'Тайный покупатель'
        elif self.is_staff:
            return 'Персонал'

    @property
    def profile(self):
        if self.is_customer:
            return self.customer_profile
        elif self.is_performer:
            return self.performer_profile
        else:
            return None

    def save(self, *args, **kwargs):
        """ Add user type validation """
        if not self.is_customer and not self.is_performer and not self.is_staff:
            raise ValidationError('Пользователь должен быть тайным покупателем, заказчиком или персоналом')
        super().save(*args, **kwargs)

    def get_full_name(self):
        """ Get user full name """
        full_name = ''

        if self.last_name:
            full_name += self.last_name.capitalize() + ' '

        if self.first_name:
            full_name += self.first_name.capitalize() + ' '

        if self.patronymic:
            full_name += self.patronymic

        return full_name.strip() or 'Не указано'

    def get_absolute_url(self):

        return reverse('profile:detail', args=(self.id, ))


class PerformerProfile(models.Model):
    """ """

    education_types = (
        ('Higher', 'Высшее'),
        ('Pre-Higher', 'Неоконченное высшее'),
        ('College', 'Средне-специальное'),
        ('School', 'Среднее'),
        ('Pre-school', 'Неоконченное среднее')
    )
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name='performer_profile', verbose_name='Пользователь')
    birth_date = models.DateField(null=True, blank=True, verbose_name='Дата рождения')
    city = models.ForeignKey(
        'core.City', on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Город проживания')
    work_cities = models.ManyToManyField(
        'core.City', blank=True, related_name='working_cities',
        verbose_name='Города в которых можетe проводить проверки')
    education = models.CharField(
        max_length=30, choices=education_types, default=None, null=True, blank=True, verbose_name='Образование')
    work_place = models.CharField(max_length=150, blank=True, verbose_name='Место работы')
    position = models.CharField(max_length=150, blank=True, verbose_name='Должность')
    additional = models.TextField(blank=True, verbose_name='Дополнительная информация')
    staff_comment = models.TextField(blank=True, verbose_name='Комментарии персонала')

    is_approved = models.BooleanField(default=False, verbose_name='Анкета одобрена')

    class Meta:
        verbose_name = 'Тайный покупатель'
        verbose_name_plural = 'Тайные покупатели'

    @property
    def age(self):
        return relativedelta(date.today(), self.birth_date).years

    @property
    def autos_list(self):
        autos = ''
        for auto in self.autos.all():
            autos += auto.__str__() + ', '
        return autos.strip(', ')

    def __str__(self):
        return self.user.get_full_name()

    def approve(self):
        pass


class PerformerAuto(models.Model):
    """ """
    performer_profile = models.ForeignKey(
        PerformerProfile, on_delete=models.CASCADE, related_name='autos', verbose_name='Профиль исполнителя')
    brand = models.ForeignKey('core.CarBrand', on_delete=models.CASCADE, related_name='autos', verbose_name='Марка авто')
    model = models.ForeignKey('core.CarModel', on_delete=models.CASCADE, related_name='autos', verbose_name='Модель')
    built_year = models.PositiveIntegerField(default=1990, verbose_name='Год выпуска')
    owns_from = models.PositiveIntegerField(default=1990,  verbose_name='В собственности с')

    class Meta:
        verbose_name = 'Транспортное средство'
        verbose_name_plural = 'Транспортные средства'

    def __str__(self):
        return '{} {} ({} г. в.)'.format(self.brand.name, self.model.name, self.built_year)


class PerformerApproveRequest(models.Model):
    """ """

    status = models.CharField(max_length=20, choices=list(ApprovalRequestStatusesEnum.values.items()),
                              default=ApprovalRequestStatusesEnum.ACTIVE, verbose_name='Статус')
    performer_profile = models.OneToOneField(PerformerProfile, on_delete=models.CASCADE, related_name='approve_request',
                                             verbose_name='Профиль')
    was_declined = models.BooleanField(default=False)
    notes = models.CharField(max_length=500, blank=True, null=True, verbose_name='Замечания')

    class Meta:
        verbose_name = 'Заявка на одобрение профиля'
        verbose_name_plural = 'Заявки на одобрение профилей'

    def approve(self):
        """ """
        self.performer_profile.is_approved = True
        self.performer_profile.save()
        self.delete()

    def decline(self):
        self.status = ApprovalRequestStatusesEnum.DECLINED
        self.was_declined = True
        self.save()


class CustomerProfile(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name='customer_profile', verbose_name='Пользователь')
    organisation_tree_node = models.ForeignKey(
        'organisation_tree.OrganisationTreeNode', on_delete=models.SET_NULL,
        null=True, blank=True, verbose_name='Место работы', related_name='employee_profiles')

    @property
    def is_boss(self):
        return self.organisation_tree_node == self.organisation_tree_node.get_root()



