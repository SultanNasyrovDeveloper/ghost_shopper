import json

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.shortcuts import Http404, get_object_or_404, render
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.generic import View

from ghost_shopper.auth.decorators import staff_member_required
from ghost_shopper.checklist.enums import QUESTION_TYPES
from ghost_shopper.checklist.models import (
    Checklist, IntegerChoicesAnswer, IntegerQuestionOption, OpenAnswer,
    Question, Section, TextChoicesAnswer, TextQuestionOption)

from .forms import (GeneralAnswerForm, IntQuestionOptionForm, QuestionForm,
                    SectionForm, TextQuestionOptionForm)
from .serializers import (ChecklistSerializer, IntegerQuestionOptionSerializer,
                          QuestionSerializer, SectionSerializer,
                          TextQuestionOptionSerializer)


@method_decorator(staff_member_required, name='dispatch')
class ChecklistConstructorView(LoginRequiredMixin, View):
    """Checklist constructor view."""
    
    login_url = reverse_lazy('auth:login')

    def get(self, request, *args, **kwargs):
        context = dict()
        checklist = get_object_or_404(Checklist, id=kwargs.pop('pk'))
        context['checklist'] = checklist
        context['checklist_json'] = json.dumps(ChecklistSerializer(checklist).data)
        context['question_types_json'] = json.dumps(QUESTION_TYPES)
        context['section_form'] = SectionForm()
        context['question_form'] = QuestionForm()
        context['general_answer_form'] = GeneralAnswerForm()
        context['int_option_form'] = IntQuestionOptionForm()
        context['text_option_form'] = TextQuestionOptionForm()
        return render(request, 'checklist/constructor/constructor.html', context)


@login_required(login_url=reverse_lazy('auth:login'))
@staff_member_required
def create_section(request):
    """ Create section ajax view """

    if request.method == 'POST':
        data = json.loads(request.body)
        form = SectionForm(data=data['form_data'])

        if form.is_valid():
            instance = form.save()
            response = {'status': 200, 'section': json.dumps(SectionSerializer(instance).data)}
            if form.cleaned_data['upper_section_id']:
                response['upper_section'] = form.cleaned_data['upper_section_id']
            return JsonResponse(response)

        return JsonResponse({'status': 400, 'errors': form.errors})

    raise Http404


@login_required(login_url=reverse_lazy('auth:login'))
@staff_member_required
def delete_section(request):
    """ Delete section ajax view """

    if request.method == 'POST':

        data = json.loads(request.body)

        try:
            section = Section.objects.get(id=data['section_id'])
            response = {'section': section.id}
        except Section.DoesNotExist:
            response = {
                'status': 400,
                'errors': 'Такой секции не существует. Перезагрузите страницу.'
            }
            return JsonResponse(response)

        section.delete()

        response['status'] = 200
        return JsonResponse(response)

    else:
        raise Http404


@login_required(login_url=reverse_lazy('auth:login'))
@staff_member_required
def delete_question(request):
    """ Delete question ajax view """

    if request.method == 'POST':

        data = json.loads(request.body)

        try:
            question = Question.objects.get(id=data['question_id'])
        except Question.DoesNotExist:
            response = {
                'status': 400,
                'errors': 'Такого вопроса не существует. Перезагрузите страницу.'}
            return JsonResponse(response)

        response = {
            'question_id': question.id,
            'section_id': question.section_id
        }
        question.delete()
        response['status'] = 200
        return JsonResponse(response)
    else:
        raise Http404


@login_required(login_url=reverse_lazy('auth:login'))
@staff_member_required
def create_general_question(request):
    """ Create general question ajax view """
    if request.method == 'POST':

        data = json.loads(request.body)
        question_form = QuestionForm(data['question_data'])

        if question_form.is_valid():
            answer_form = GeneralAnswerForm(data['answer_data'])
            if answer_form.is_valid():
                question = question_form.save()
                answer_form.cleaned_data['question_id'] = question.id
                answer_form.save()

                response = {
                    'question': QuestionSerializer(question).data,
                    'status': 200,
                }

                if data['question_data'].get('upper_question_id', None):
                    upper_question = Question.objects.get(id=int(data['question_data'].get('upper_question_id')))
                    question.below(upper_question)
                    question.save()
                    response['upper_question'] = data['question_data'].get('upper_question_id')

                return JsonResponse(response)
            else:
                response = {
                    'status': 400,
                    'errors': answer_form.errors
                }
                return JsonResponse(response)
        else:
            response = {
                'status': 400,
                'errors': question_form.errors
            }
            return JsonResponse(response)

    else:
        raise Http404


@login_required(login_url=reverse_lazy('auth:login'))
@staff_member_required
def create_open_question(request):
    """ """

    if request.method == 'POST':

        data = json.loads(request.body)
        question_form = QuestionForm(data['question_data'])

        if question_form.is_valid():
            question = question_form.save()
            OpenAnswer.objects.create(question=question)

            response = {
                'question': QuestionSerializer(question).data,
                'status': 200,
            }

            if data['question_data'].get('upper_question_id', None):
                upper_question = Question.objects.get(id=int(data['question_data'].get('upper_question_id')))
                question.below(upper_question)
                question.save()
                response['upper_question'] = data['question_data'].get('upper_question_id')

            return JsonResponse(response)
        else:
            response = {
                'status': 400,
                'error_message': ' '.join([error for error in question_form.errors['__all__']])
            }
            return JsonResponse(response)

    else:
        raise Http404


@login_required(login_url=reverse_lazy('auth:login'))
@staff_member_required
def create_int_choices_question(request):
    """ Create int choices question """
    if request.method == 'POST':
        data = json.loads(request.body)
        question_form = QuestionForm(data['question_data'])

        if question_form.is_valid():
            question = question_form.save()
            IntegerChoicesAnswer.objects.create(question=question)

            response = {
                'question': QuestionSerializer(question).data,
                'status': 200,
            }

            if data['question_data'].get('upper_question_id', None):
                upper_question = Question.objects.get(id=int(data['question_data'].get('upper_question_id')))
                question.below(upper_question)
                question.save()
                response['upper_question'] = data['question_data'].get('upper_question_id')

            return JsonResponse(response)
        else:
            response = {
                'status': 400,
                'errors': question_form.errors
            }
            return JsonResponse(response)
    else:
        raise Http404


@login_required(login_url=reverse_lazy('auth:login'))
@staff_member_required
def create_text_choices_question(request):
    """ Create etxt choices question """
    if request.method == 'POST':

        data = json.loads(request.body)
        question_form = QuestionForm(data['question_data'])

        if question_form.is_valid():
            question = question_form.save()
            TextChoicesAnswer.objects.create(question=question)

            response = {
                'question': QuestionSerializer(question).data,
                'status': 200,
            }

            if data['question_data'].get('upper_question_id', None):
                upper_question = Question.objects.get(id=int(data['question_data'].get('upper_question_id')))
                question.below(upper_question)
                question.save()
                response['upper_question'] = data['question_data'].get('upper_question_id')

            return JsonResponse(response)
        else:
            response = {
                'status': 400,
                'error_message': question_form.errors
            }
            return JsonResponse(response)

    else:
        raise Http404


@login_required(login_url=reverse_lazy('auth:login'))
@staff_member_required
def create_int_option(request):
    """ Create integer question option """
    if request.method == 'POST':

        data = json.loads(request.body)
        form = IntQuestionOptionForm(data['option_data'])
        if form.is_valid():
            option = form.save()
            response = {
                'option': IntegerQuestionOptionSerializer(option).data,
                'status': 200,
            }
            if data['option_data'].get('upper_option_id', None):
                response['upper_option'] = data['option_data']['upper_option_id']
            return JsonResponse(response)
        else:
            response = {
                'status': 400,
                'error_message': form.errors
            }
            return JsonResponse(response)

    else:
        raise Http404


@login_required(login_url=reverse_lazy('auth:login'))
@staff_member_required
def create_text_option(request):
    """ Create text option """

    if request.method == 'POST':
        data = json.loads(request.body)
        form = TextQuestionOptionForm(data['option_data'])
        if form.is_valid():
            option = form.save()
            response = {
                'option': TextQuestionOptionSerializer(option).data,
                'status': 200,
            }
            if data['option_data'].get('upper_option_id', None):
                response['upper_option'] = data['option_data']['upper_option_id']
            return JsonResponse(response)
        else:
            response = {
                'status': 400,
                'error_message': form.errors
            }
            return JsonResponse(response)
    else:
        raise Http404


@login_required(login_url=reverse_lazy('auth:login'))
@staff_member_required
def delete_option(request):
    """ Delete option """
    if request.method == 'POST':

        data = json.loads(request.body)
        if data['question_type'] == QUESTION_TYPES['INT_CHOICES']:
            option = IntegerQuestionOption.objects.get(id=int(data['option_id']))
        else:
            option = TextQuestionOption.objects.get(id=int(data['option_id']))
        response = {
            'question_id' : option.question_id,
            'option': option.id
        }
        option.delete()
        response['status'] = 200
        return JsonResponse(response)
    else:
        raise Http404
