# Generated by Django 2.2.3 on 2019-11-13 11:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('checklist', '0008_auto_20191113_1424'),
    ]

    operations = [
        migrations.AlterField(
            model_name='checklist',
            name='excel_file',
            field=models.FileField(default='', upload_to=''),
        ),
    ]
