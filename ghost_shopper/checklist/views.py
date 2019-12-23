import json
import mimetypes
import os
from wsgiref.util import FileWrapper

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http import JsonResponse, StreamingHttpResponse
from django.shortcuts import Http404, get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views import generic

from ghost_shopper.check.enums import CheckStatusesEnum

from . import forms, models
from .enums import QUESTION_TYPES
from .formset import ChecklistFormset
from .questions_counter import QuestionsCounter


class ChecklistDetailView(LoginRequiredMixin, UserPassesTestMixin, generic.DetailView):
    """Checklist Detail view."""

    model = models.Checklist
    template_name = 'checklist/detail.html'
    login_url = reverse_lazy('auth:login')

    def test_func(self):
        """Test that request user can access this view."""
        user = self.request.user
        check = get_object_or_404(models.Checklist, id=self.kwargs.get('pk', None)).check_obj

        if user.is_performer:
            return check.performer == user
        elif user.is_customer:
            customer_organisation = user.profile.organisation_tree_node
            return check.target_id in customer_organisation.get_descendants_ids()
        elif user.is_staff:
            if user.is_superuser:
                return True
            return user == check.curator
        return False

    def get_context_data(self, **kwargs):
        """Add data to page context."""
        context = super().get_context_data(**kwargs)
        context['question_types'] = QUESTION_TYPES
        context['sections'] = self.get_object().sections.filter(parent=None)
        context['counter'] = QuestionsCounter()
        return context


class ChecklistUpdateView(LoginRequiredMixin, UserPassesTestMixin, generic.View):
    """Checklist update view."""

    login_url = reverse_lazy('auth:login')
    template_name = 'checklist/update.html'

    def test_func(self):
        """Test that request user can access this view."""
        user = self.request.user
        check = get_object_or_404(models.Checklist, id=self.kwargs.get('pk', None)).check_obj

        if user.is_customer:
            return check.target.get_root() == user.profile.organisation_tree_node

        elif user.is_performer:
            return check.performer == user and check.status == CheckStatusesEnum.PROCESSING

        elif user.is_staff:
            if user.is_superuser:
                return True
            return check.curator == user

    def get(self, request, *args, **kwargs):
        checklist = get_object_or_404(models.Checklist, id=kwargs.get('pk', None))
        formset = ChecklistFormset(checklist.id)
        context = {
            'counter': QuestionsCounter(),
            'checklist': checklist,
            'form': forms.ChecklistMediaForm(instance=checklist, prefix='media'),
            'formset': formset.formset,
            'question_types': QUESTION_TYPES,
            'check_status': CheckStatusesEnum.values,
        }

        checklist_is_valid = True
        error_message = ''
        if 'checklist_is_valid' in request.session:
            checklist_is_valid = request.session.pop('checklist_is_valid')
            error_message = request.session.pop('error_message')
        context['checklist_is_valid'] = checklist_is_valid
        context['error_message'] = error_message

        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        checklist = get_object_or_404(models.Checklist, id=kwargs.get('pk', None))
        formset = ChecklistFormset(checklist.id, request.POST)
        form = forms.ChecklistMediaForm(request.POST, request.FILES, instance=checklist, prefix='media')

        if formset.is_valid():
            formset.save()
            if form.is_valid():
                form.save()
                return redirect(reverse_lazy('check:detail', args=(checklist.check_obj_id, )))
            else:
                context = {
                    'counter': QuestionsCounter(),
                    'checklist': checklist,
                    'form': form,
                    'formset': formset.formset,
                    'question_types': QUESTION_TYPES,
                    'check_status': CheckStatusesEnum.values
                }
                return render(request, self.template_name, context)
        else:
            context = {
                'counter': QuestionsCounter(),
                'checklist': checklist,
                'form': form,
                'formset': formset.formset,
                'question_types': QUESTION_TYPES,
                'check_status': CheckStatusesEnum.values
            }
            return render(request, self.template_name, context)


class ChecklistAppealView(ChecklistUpdateView):
    template_name = 'checklist/appeal.html'

    def post(self, request, *args, **kwargs):
        checklist = get_object_or_404(models.Checklist, id=kwargs.get('pk', None))
        check = checklist.check


@login_required(login_url=reverse_lazy('auth:login'))
def delete_image(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        image = get_object_or_404(models.Image, id=data.get('image_id', None))
        image.delete()
        return JsonResponse({'status': 200})
    else:
        raise Http404


def get_checklist_audio(request, pk):
    checklist = get_object_or_404(models.Checklist, id=int(pk))
    the_file = checklist.audio.path
    chunk_size = 8192
    response = StreamingHttpResponse(
        FileWrapper(open(the_file, 'rb'), chunk_size), content_type=mimetypes.guess_type(the_file)[0]
    )

    response['Content-Type'] = 'audio/mp3'
    response['Content-Length'] = os.path.getsize(checklist.audio.path)
    response['Accept-Ranges'] = 'bytes'
    return response
