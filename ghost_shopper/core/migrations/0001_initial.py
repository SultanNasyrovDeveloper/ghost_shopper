# Generated by Django 2.2.3 on 2019-12-23 14:46

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='CarBrand',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, verbose_name='Название')),
            ],
        ),
        migrations.CreateModel(
            name='CheckKind',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=1000, verbose_name='Название')),
                ('price', models.SmallIntegerField(default=0, verbose_name='Цена')),
            ],
        ),
        migrations.CreateModel(
            name='City',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=70, verbose_name='Название')),
            ],
            options={
                'verbose_name': 'Город',
                'verbose_name_plural': 'Города',
            },
        ),
        migrations.CreateModel(
            name='MyOrganisation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('full_name', models.CharField(blank=True, max_length=1000, null=True, verbose_name='Полное название')),
                ('short_name', models.CharField(blank=True, max_length=500, null=True, verbose_name='Сокращенное название')),
                ('INN', models.CharField(blank=True, max_length=50, null=True, verbose_name='ИНН')),
                ('KPP', models.CharField(blank=True, max_length=50, null=True, verbose_name='КПП')),
                ('account', models.CharField(blank=True, max_length=50, null=True, verbose_name='Расчетный счет')),
                ('address', models.CharField(blank=True, max_length=1000, null=True, verbose_name='Юридический адрес')),
                ('phone_number', models.CharField(blank=True, max_length=50, null=True, verbose_name='Номер телефона')),
                ('bank_name', models.CharField(blank=True, max_length=1000, null=True, verbose_name='Название банка')),
                ('bank_BIC', models.CharField(blank=True, max_length=25, null=True, verbose_name='БИК банка')),
                ('bank_account', models.CharField(blank=True, max_length=50, null=True, verbose_name='Расчетный счет банка')),
            ],
        ),
        migrations.CreateModel(
            name='PerformerLettersTemplates',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('invite_message', models.TextField(default='Уважаемый, {performer}! \nПредлагаем Вам провести {check}.\n{link}')),
                ('apply_message', models.TextField(default='Уважаемый, {performer}! \nВас одобрили для проведения проверки {check}.\n{link}')),
            ],
        ),
        migrations.CreateModel(
            name='CarModel',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='Название')),
                ('brand', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='models', to='core.CarBrand', verbose_name='Марка')),
            ],
        ),
    ]
