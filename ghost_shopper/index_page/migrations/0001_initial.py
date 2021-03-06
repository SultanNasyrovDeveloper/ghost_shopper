# Generated by Django 2.2.3 on 2019-12-23 14:46

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='CallbackForm',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('processed', models.BooleanField(default=False, verbose_name='Обработана')),
                ('name', models.CharField(max_length=50, verbose_name='Имя')),
                ('phone_number', models.CharField(max_length=20, verbose_name='Номер телефона')),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='Время создания')),
            ],
        ),
        migrations.CreateModel(
            name='IndexPage',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(blank=True, help_text='Значение тега <title></title>', max_length=500, null=True, verbose_name='Заголовок')),
                ('keywords', models.CharField(blank=True, help_text='Значение аттрибута content тега <meta name="keywords" content="">', max_length=500, null=True, verbose_name='Ключевые слова')),
                ('description', models.CharField(blank=True, help_text='Значение аттрибута content тега <meta name="description" content="">', max_length=1000, null=True, verbose_name='Описание')),
                ('logo', models.FileField(blank=True, null=True, upload_to='logo/')),
                ('phone_number', models.CharField(blank=True, max_length=20, null=True, verbose_name='Номер телефона')),
                ('email', models.EmailField(blank=True, max_length=150, null=True)),
                ('header_background', models.ImageField(blank=True, null=True, upload_to='index/')),
                ('header_tagline', models.CharField(blank=True, max_length=200, null=True)),
                ('header_subtagline', models.CharField(blank=True, max_length=400, null=True)),
                ('company_name', models.CharField(blank=True, max_length=250, null=True, verbose_name='Название компании')),
                ('about_text', models.CharField(blank=True, max_length=1000, null=True, verbose_name='Текст о компании')),
            ],
        ),
        migrations.CreateModel(
            name='WorkingStep',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order', models.PositiveSmallIntegerField(unique=True, verbose_name='Порядковый номер')),
                ('name', models.CharField(max_length=250, verbose_name='Название шага')),
                ('description', models.CharField(max_length=1000, verbose_name='Описание')),
            ],
            options={
                'ordering': ('order',),
            },
        ),
    ]
