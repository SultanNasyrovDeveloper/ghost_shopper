# Generated by Django 2.2.3 on 2019-09-29 12:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('check', '0003_auto_20190929_1258'),
    ]

    operations = [
        migrations.AlterField(
            model_name='check',
            name='deadline',
            field=models.DateField(blank=True, null=True, verbose_name='Дедлайн'),
        ),
        migrations.AlterField(
            model_name='check',
            name='start_date',
            field=models.DateField(blank=True, null=True, verbose_name='Дата начала'),
        ),
    ]
