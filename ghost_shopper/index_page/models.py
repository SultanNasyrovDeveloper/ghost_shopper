from django.db import models


class IndexPage(models.Model):

    # SEO
    title = models.CharField(
        max_length=500, verbose_name='Заголовок', help_text='Значение тега <title></title>', null=True, blank=True)
    keywords = models.CharField(
        max_length=500, verbose_name='Ключевые слова', null=True, blank=True,
        help_text='Значение аттрибута content тега <meta name="keywords" content="">')
    description = models.CharField(
        max_length=1000, verbose_name='Описание', null=True, blank=True,
        help_text='Значение аттрибута content тега <meta name="description" content="">')

    # navbar
    logo = models.FileField(upload_to='logo/', null=True, blank=True)
    phone_number = models.CharField(max_length=20, verbose_name='Номер телефона', null=True, blank=True)
    email = models.EmailField(max_length=150, null=True, blank=True)

    # first block
    header_background = models.ImageField(upload_to='index/', null=True, blank=True)
    header_tagline = models.CharField(max_length=200, null=True, blank=True)
    header_subtagline = models.CharField(max_length=400, null=True, blank=True)

    company_name = models.CharField(max_length=250, verbose_name='Название компании', null=True, blank=True)
    about_text = models.CharField(max_length=1000, verbose_name='Текст о компании', null=True, blank=True)

    def __str__(self):
        return self.title

    @classmethod
    def load(cls):
        page, _ = cls.objects.get_or_create(id=1)
        return page

    def save(self, *args, **kwargs):
        self.id = 1
        return super().save(*args, **kwargs)


class WorkingStep(models.Model):
    order = models.PositiveSmallIntegerField(unique=True, verbose_name='Порядковый номер')
    name = models.CharField(max_length=250, verbose_name='Название шага')
    description = models.CharField(max_length=1000, verbose_name='Описание')

    def __str__(self):
        return 'Шаг {}: {}'.format(self.order, self.name)

    class Meta:
        ordering = ('order', )


class CallbackForm(models.Model):
    processed = models.BooleanField(default=False, verbose_name='Обработана')
    name = models.CharField(max_length=50, verbose_name='Имя')
    phone_number = models.CharField(max_length=20, verbose_name='Номер телефона')
    created = models.DateTimeField(auto_now_add=True, verbose_name='Время создания')

    def __str__(self):
        return 'Заявка на обратный звонок: {} - {}({})'.format(self.name, self.phone_number, self.created)

