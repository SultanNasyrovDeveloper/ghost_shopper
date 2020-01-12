from django.db import models
from django.db.models import Max, Sum
from django.db.models.signals import post_save
from django_cloneable import CloneableMixin
from ordered_model.models import OrderedModel

from ghost_shopper.check.models import Check

from .enums import QUESTION_TYPES


class Checklist(models.Model):
    """ Checklist """
    check_obj = models.OneToOneField('check.Check', on_delete=models.CASCADE,
                                     related_name='checklist', verbose_name='Проверка')
    type = models.CharField(max_length=20, null=True, blank=True, verbose_name='Тип')
    audio = models.FileField(upload_to='checklist_audio/', null=True, blank=True, verbose_name='Аудиозапись')
    visit_date = models.DateField(null=True, blank=True, verbose_name='Дата визита')

    class Meta:
        verbose_name = 'чеклист'
        verbose_name_plural = 'чеклисты'

    def __str__(self):
        return 'Чеклист {}'.format(self.id)

    @property
    def name(self):
        return 'Чек-лист {}'.format(self.check_obj.title)

    def clone(self, check):

        sections = self.sections.filter(parent=None)

        new_checklist = self
        new_checklist.id = None
        new_checklist.check_obj = check
        new_checklist.save()

        for section in sections:
            section.clone(new_checklist)

        return new_checklist

    def get_statistics(self):
        """ Get statistic data for this checklist """
        statistics = {'points_total': 0, 'points': 0, 'sections': {}}

        for section in self.sections.all():
            statistics['sections'][section.name.value] = section.get_statistics()
            section_data = statistics['sections'][section.name.value]
            statistics['points_total'] += section_data['points_total']
            statistics['points'] += section_data['points']

        return statistics


def create_checklist(sender, **kwargs):
    if kwargs.get('created', None):
        Checklist.objects.create(check_obj=kwargs.get('instance'))


post_save.connect(create_checklist, sender=Check)


class SectionName(models.Model):
    """  """
    value = models.CharField(max_length=150, unique=True, verbose_name='Название секции')

    class Meta:
        verbose_name = 'название секции'
        verbose_name_plural = 'названия секций'

    def __str__(self):
        return self.value


class Section(OrderedModel):
    """ Checklist section """

    checklist = models.ForeignKey(Checklist, on_delete=models.CASCADE, related_name='sections', verbose_name='Чеклист')
    name = models.ForeignKey(SectionName, on_delete=models.CASCADE, related_name='sections',
                             null=True, blank=True, verbose_name='Название секции')

    # TODO сделать проверку при сохранении - нельзя создавать подмодуль у подмодуля. Ограничение уровней
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='subsections',
                               verbose_name='Родитель')

    order_with_respect_to = 'checklist'

    class Meta(OrderedModel.Meta):
        unique_together = ('checklist', 'name')
        verbose_name = 'секция'
        verbose_name_plural = 'секции'

    def __str__(self):
        return 'Чеклист {} - Секция: {}'.format(self.checklist_id, self.name.value)

    def is_leaf(self):
        """ """
        return True if self.parent else False

    def clone(self, checklist, parent=None):
        """  """
        questions = self.questions.all()
        subsections = self.subsections.all()

        new_section = self
        new_section.id = None
        new_section.parent = parent
        new_section.checklist = checklist
        new_section.save()

        for question in questions.all():
            question.clone(new_section)

        for subsection in subsections.all():
            subsection.clone(checklist, new_section)

        return new_section

    def get_statistics(self):
        """ Dict objects with statistics for this section """
        section = {}
        section['points_total'] = self._get_total_points()
        section['points'] = self._get_points()
        section['subsections'] = {}

        if self.parent:
            for subsection in self.subsections.all():
                section['subsections'][subsection.name.value] = {'points_total': 0, 'points': 0}
                subsection_dict = section['subsections'][subsection.name.value]
                subsection_stats = subsection.get_statistics()
                subsection_dict['points_total'] += subsection_stats['points_total']
                subsection_dict['points'] += subsection_stats['points']
        return section

    def _get_total_points(self):
        """ Get total number of points that can be in the section """
        general_questions_total = list(self.questions.filter(type=QUESTION_TYPES['GENERAL']).aggregate(
            Sum('general_answer__positive_answer_value')).values())
        general_questions_total = general_questions_total[0] if general_questions_total[0] else 0

        int_choices_questions_total = list(self.questions.filter(type=QUESTION_TYPES['INT_CHOICES']).annotate(
            max_points=Max('int_options__points')).aggregate(Sum('max_points')).values())
        int_choices_questions_total = int_choices_questions_total[0] if int_choices_questions_total[0] else 0

        return general_questions_total + int_choices_questions_total

    def _get_points(self):
        """ Get number of points that this section got according to answered questions """
        general_questions_points = list(self.questions.filter(
            type=QUESTION_TYPES['GENERAL'], general_answer__answer=True).aggregate(
            Sum('general_answer__positive_answer_value')).values())
        general_questions_points = general_questions_points[0] if general_questions_points[0] else 0

        int_choices_questions_points = list(self.questions.filter(type=QUESTION_TYPES['INT_CHOICES']).annotate(
            points=Max('int_choices_answer__answer__points')).aggregate(Sum('points')).values())
        int_choices_questions_points = int_choices_questions_points[0] if int_choices_questions_points[0] else 0

        return general_questions_points + int_choices_questions_points


class Question(OrderedModel):
    """ Checklist question """
    section = models.ForeignKey(Section, on_delete=models.CASCADE, related_name='questions', verbose_name='Секция')
    text = models.CharField(max_length=1500, verbose_name='Текст Вопроса')
    type = models.CharField(max_length=50, verbose_name='Тип')

    order_with_respect_to = 'section'

    class Meta(OrderedModel.Meta):
        verbose_name = 'вопрос'
        verbose_name_plural = 'вопросы'

    def __str__(self):
        return self.text

    @property
    def answer(self):
        """ Returns question answer according to the type """
        if self.type == QUESTION_TYPES['GENERAL']:
            return self.general_answer
        elif self.type == QUESTION_TYPES['OPEN']:
            return self.open_answer
        elif self.type == QUESTION_TYPES['INT_CHOICES']:
            return self.int_choices_answer
        elif self.type == QUESTION_TYPES['TEXT_CHOICES']:
            return self.text_choices_answer

    @property
    def is_answered(self):
        if self.type == QUESTION_TYPES['GENERAL'] or self.type == QUESTION_TYPES['OPEN']:
            return self.answer.answer is not None
        elif self.type == QUESTION_TYPES['INT_CHOICES'] or self.type == QUESTION_TYPES['TEXT_CHOICES']:
            return hasattr(self.answer, 'answer')

    @property
    def options(self):
        if self.type == QUESTION_TYPES['INT_CHOICES']:
            return self.int_options.all()
        elif self.type == QUESTION_TYPES['TEXT_CHOICES']:
            return self.text_options.all()
        else:
            return []

    def clone(self, section):
        """ Clones current question and invokes clone methods for answer and option if there are options """
        answer = self.answer
        options = self.options

        new_question = self
        new_question.id = None
        new_question.section = section
        new_question.save()

        answer.clone(question=new_question)

        for option in options:
            option.clone(new_question)

        return new_question


class IntegerQuestionOption(OrderedModel):
    """  Integer choices question option """
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='int_options', verbose_name='Вопрос')
    value = models.PositiveSmallIntegerField(default=0, verbose_name='Значение')
    points = models.PositiveSmallIntegerField(default=0, verbose_name='Баллов')

    order_with_respect_to = 'question'

    class Meta(OrderedModel.Meta):
        verbose_name = 'Числовой вариант'
        verbose_name_plural = 'Числовые варианты'

    def __str__(self):
        return str(self.value)

    def clone(self, question):
        new_option = self
        new_option.id = None
        new_option.question = question
        new_option.save()
        return new_option


class TextQuestionOption(OrderedModel):
    """  Text choices question option """
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='text_options', verbose_name='Вопрос')
    value = models.CharField(max_length=150, verbose_name='Значение')

    order_with_respect_to = 'question'

    class Meta(OrderedModel.Meta):
        verbose_name = 'Текстовый вариант'
        verbose_name_plural = 'Текстовые варианты'

    def __str__(self):
        return str(self.value)

    def clone(self, question):
        new_option = self
        new_option.id = None
        new_option.question = question
        new_option.save()
        return new_option


class Answer(models.Model):
    """ Base answer class """
    performer_comment = models.TextField(null=True, blank=True, verbose_name='Комментарий испольнителя')
    appeal_comment = models.TextField(null=True, blank=True, verbose_name='Текст апелляции')
    appeal_answer = models.TextField(null=True, blank=True, verbose_name='Ответ на аппеляцию')

    class Meta:
        abstract = True

    def clone(self, question):
        return NotImplementedError

    @property
    def value(self):
        """ Get answer value """
        return NotImplementedError

    def get_answer_options(self):
        """ """
        return NotImplementedError


class GeneralAnswer(Answer):
    """ General answer """
    question = models.OneToOneField(Question, on_delete=models.CASCADE, related_name='general_answer')
    answer = models.NullBooleanField(default=None, null=True, verbose_name='Ответ')
    positive_answer_value = models.PositiveSmallIntegerField(default=1, verbose_name='Баллов за положительный ответ')

    class Meta:
        verbose_name = 'Общий ответ'
        verbose_name_plural = 'Общие ответы'

    def __str__(self):
        return 'Ответ на вопрос {}: {}'.format(self.question.text, self.answer)

    @property
    def value(self):
        if self.answer is True:
            return self.positive_answer_value
        else:
            return 0

    def get_answer_options(self):
        return '{} - выполнено/ 0 - не выполнено'.format(self.positive_answer_value)

    def clone(self, question):
        new_answer = self
        new_answer.id = None
        new_answer.question = question
        new_answer.save()
        return new_answer


class OpenAnswer(Answer):
    """ Open answer """
    question = models.OneToOneField(Question, on_delete=models.CASCADE, related_name='open_answer')
    answer = models.CharField(max_length=100, null=True, blank=True, verbose_name='Ответ')

    class Meta:
        verbose_name = 'Открытый ответ'
        verbose_name_plural = 'Открытые ответы'

    def __str__(self):
        return 'Ответ на вопрос {}: {}'.format(self.question.text, self.answer)

    @property
    def value(self):
        return self.answer

    def get_answer_options(self):
        return 'Развернутый ответ'

    def clone(self, question):
        new_answer = self
        new_answer.id = None
        new_answer.question = question
        new_answer.save()
        return new_answer


class IntegerChoicesAnswer(Answer):
    """ Integer choices answer
    TODO Валдировать поле answer при сохранение на вхождение в список всех возможных вариантов
    """
    question = models.OneToOneField(Question, on_delete=models.CASCADE, related_name='int_choices_answer')
    answer = models.OneToOneField(IntegerQuestionOption, on_delete=models.SET_NULL, null=True, blank=True,
                                  verbose_name='Ответ')

    class Meta:
        verbose_name = 'Ответ с числовыми вариантами'
        verbose_name_plural = 'Ответы с числовыми вариантами'

    def __str__(self):
        return 'Ответ на вопрос {}: {}'.format(self.question.text, self.answer)

    @property
    def value(self):
        return self.answer.points if self.answer else 0

    def get_answer_options(self):
        options = ['{} - {} баллов'.format(option.value, option.points) for option in self.question.int_options.all()]
        return '/'.join(options)

    def clone(self, question):
        new_answer = self
        new_answer.id = None
        new_answer.answer = None
        new_answer.question = question
        new_answer.save()
        return new_answer


class TextChoicesAnswer(Answer):
    """ Text choices answer """
    question = models.OneToOneField(Question, on_delete=models.CASCADE, related_name='text_choices_answer')
    answer = models.OneToOneField(TextQuestionOption, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Ответ')

    class Meta:
        verbose_name = 'Ответ с текстовыми вариантами'
        verbose_name_plural = 'Ответы с текстовыми вариантами'

    def __str__(self):
        return 'Ответ на вопрос {}: {}'.format(self.question.text, self.answer)

    def get_answer_options(self):
        return '/'.join([option.value for option in self.question.text_options.all()])

    @property
    def value(self):
        return self.answer.value if self.answer else 'Не выбран'

    def clone(self, question):
        new_answer = self
        new_answer.id = None
        new_answer.answer = None
        new_answer.question = question
        new_answer.save()
        return new_answer


class Image(models.Model):
    """ Checklist image """

    checklist = models.ForeignKey(Checklist, on_delete=models.CASCADE, verbose_name='Чеклист', related_name='images')
    file = models.FileField(upload_to='checklist_images/', verbose_name='Изображение')

    class Meta:
        verbose_name = 'Изображение'
        verbose_name_plural = 'Изображения'

    def __str__(self):
        return
