from django.db import models
from django.db.models.signals import post_save

from ghost_shopper.user_profile.models import User


class NewsFeed(models.Model):
    user = models.OneToOneField('user_profile.User', on_delete=models.CASCADE, related_name='news_feed')
    news = models.ManyToManyField('News')


class News(models.Model):

    body = models.TextField(verbose_name='Тело новости')
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('-created', )
        verbose_name = ''
        verbose_name_plural = ''


def create_news_feed(sender, **kwargs):
    if kwargs.get('created'):
        NewsFeed.objects.create(user=kwargs.get('instance'))


post_save.connect(create_news_feed, sender=User)

