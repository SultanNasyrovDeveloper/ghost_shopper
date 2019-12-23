# Generated by Django 2.2.3 on 2019-11-24 08:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('organisation_tree', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='organisationtreenode',
            name='INN',
            field=models.CharField(blank=True, help_text='Для отчетов', max_length=1000, null=True, verbose_name='ИНН'),
        ),
        migrations.AddField(
            model_name='organisationtreenode',
            name='KPP',
            field=models.CharField(blank=True, help_text='Для отчетов', max_length=1000, null=True, verbose_name='КПП'),
        ),
        migrations.AddField(
            model_name='organisationtreenode',
            name='checks_theme',
            field=models.CharField(blank=True, help_text='Для отчетов', max_length=1000, null=True, verbose_name='Тема проверок'),
        ),
        migrations.AddField(
            model_name='organisationtreenode',
            name='contract_name',
            field=models.CharField(blank=True, help_text='Для отчетов, Например: Договор № 8/4 – КАН-АВТО от «01» марта 2016 г.', max_length=1000, null=True, verbose_name='Тема проверок'),
        ),
        migrations.AddField(
            model_name='organisationtreenode',
            name='full_name',
            field=models.CharField(blank=True, help_text='Для отчетов', max_length=1000, null=True, verbose_name='Полное имя'),
        ),
        migrations.AddField(
            model_name='organisationtreenode',
            name='legal_address',
            field=models.CharField(blank=True, help_text='Для отчетов', max_length=1000, null=True, verbose_name='Юридический адрес'),
        ),
        migrations.AlterField(
            model_name='organisationtreenode',
            name='address',
            field=models.CharField(blank=True, max_length=250, null=True, verbose_name='Адрес'),
        ),
    ]
