# Generated by Django 2.2.3 on 2019-12-21 23:02

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('organisation_tree', '0012_auto_20191222_0158'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='OrganisationDocuments',
            new_name='OrganisationDocumentsContainer',
        ),
    ]
