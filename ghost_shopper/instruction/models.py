from django.db import models
from django.shortcuts import reverse


class Instruction(models.Model):

    name = models.CharField(max_length=150, verbose_name='Название чеклиста')
    body = models.TextField(verbose_name='Текст')

    def get_absolute_url(self):
        return reverse('instruction:detail', args=(self.id, ))

    def __str__(self):
        return self.name


