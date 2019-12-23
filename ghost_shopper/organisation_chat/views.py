import json

from datetime import datetime
from django.views import generic
from django.http import JsonResponse
from django.shortcuts import redirect, Http404, get_object_or_404

from ghost_shopper.organisation_tree.models import OrganisationTreeNode
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin

from . import models
from . import forms


class MessageCreateView(LoginRequiredMixin, UserPassesTestMixin, generic.View):

    def test_func(self):
        return True

    def post(self, request, *args, **kwargs):
        organisation = get_object_or_404(OrganisationTreeNode, id=self.kwargs.get('pk', None))
        form = forms.MessageForm(request.POST)
        if form.is_valid():
            form.save()

        return redirect(organisation.get_absolute_url())


def delete_message(request, pk):
    if request.method == 'POST':
        message = get_object_or_404(models.Message, id=int(pk))
        message.delete()
        response = {'status': 200}
        return JsonResponse(response)


def create_comment(request):
    if request.method == 'POST':
        data = json.loads(request.body)['form_data']
        form = forms.CommentForm(data=data)
        if form.is_valid():
            instance = form.save()
            image = '/static/assets/images/placeholders/placeholder.jpg'
            if instance.author.avatar:
                image = instance.author.avatar.url
            response = {
                'status': 200,
                'commentData': {
                    'id': instance.id,
                    'authorName': instance.author.get_full_name(),
                    'authorUrl': instance.author.get_absolute_url(),
                    'authorImageUrl': image,
                    'created': instance.created.strftime('%d.%m.%Y %H:%M',),
                    'body': instance.body
                }
            }
            return JsonResponse(response)
    else:
        raise Http404


def delete_comment(request, pk):
    if request.method == 'POST':
        comment = get_object_or_404(models.MessageComment, id=int(pk))
        comment.delete()
        response = {'status': 200}
        return JsonResponse(response)
    else:
        raise Http404


