# Generated by Django 2.2.3 on 2019-09-28 19:31

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Instruction',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=150, verbose_name='Название чеклиста')),
                ('body', models.TextField(verbose_name='Текст')),
            ],
        ),
    ]
