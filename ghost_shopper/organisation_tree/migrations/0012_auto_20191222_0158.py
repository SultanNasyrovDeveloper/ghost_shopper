# Generated by Django 2.2.3 on 2019-12-21 22:58

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('organisation_tree', '0011_auto_20191215_1810'),
    ]

    operations = [
        migrations.CreateModel(
            name='OrganisationDocuments',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('agreement', models.FilePathField(blank=True, max_length=250, null=True, path='/home/nasirovsultan/PycharmProjects/ghost_shopper/media/docs/')),
                ('payment', models.FilePathField(blank=True, max_length=250, null=True, path='/home/nasirovsultan/PycharmProjects/ghost_shopper/media/docs/')),
                ('organisation_node', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='organisation_tree.OrganisationTreeNode')),
            ],
        ),
        migrations.CreateModel(
            name='OrganisationMonthlyDocumentStorage',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField()),
                ('organisation', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='docs_storages', to='organisation_tree.OrganisationTreeNode')),
            ],
            options={
                'ordering': ('date',),
                'unique_together': {('organisation', 'date')},
            },
        ),
        migrations.DeleteModel(
            name='OrganisationDocument',
        ),
        migrations.AddField(
            model_name='organisationdocuments',
            name='storage',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='documents', to='organisation_tree.OrganisationMonthlyDocumentStorage'),
        ),
    ]
