# Generated by Django 2.2.3 on 2019-12-14 14:11

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('check', '0013_auto_20191214_1708'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='check',
            name='performer_typed',
        ),
    ]
