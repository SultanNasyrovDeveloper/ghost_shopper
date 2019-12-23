from django.db import models
from django.db.models.signals import post_save
from django.urls import reverse

from ghost_shopper.organisation_tree.models import OrganisationTreeNode


class Chat(models.Model):
    organisation = models.OneToOneField(
        'organisation_tree.OrganisationTreeNode', on_delete=models.CASCADE, related_name='chat', verbose_name='Чат')

    def get_absolute_url(self):
        return reverse('chat:detail', args=(self.id, ))


class Message(models.Model):
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE, related_name='messages', verbose_name='Сообщение')
    author = models.ForeignKey(
        'user_profile.User', on_delete=models.CASCADE, related_name='messages', verbose_name='Автор')
    body = models.TextField(verbose_name='Текст')
    created = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')

    class Meta:
        ordering = ('-created', )
        verbose_name = 'Сообщение'
        verbose_name_plural = 'Сообщения'

    def __str__(self):
        return 'Сообщение от {}({}): {}'.format(self.author.get_full_name(), self.created, self.body[:100])


class MessageComment(models.Model):
    message = models.ForeignKey(Message, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey('user_profile.User', on_delete=models.CASCADE)
    body = models.TextField()
    created = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')


def create_chat(sender, **kwargs):
    if kwargs.get('created', None):
        organisation_tree_node = kwargs.get('instance')
        if organisation_tree_node.level == 0:
            Chat.objects.create(organisation=organisation_tree_node)


post_save.connect(create_chat, sender=OrganisationTreeNode)
