from rest_framework.serializers import (ModelSerializer,
                                        PrimaryKeyRelatedField,
                                        SerializerMethodField,
                                        SlugRelatedField)

from ghost_shopper.checklist.enums import QUESTION_TYPES
from ghost_shopper.checklist.models import (Checklist, GeneralAnswer,
                                            IntegerChoicesAnswer,
                                            IntegerQuestionOption, OpenAnswer,
                                            Question, Section,
                                            TextChoicesAnswer,
                                            TextQuestionOption)


class IntegerQuestionOptionSerializer(ModelSerializer):
    """ """
    class Meta:
        model = IntegerQuestionOption
        fields = ('id', 'value', 'question', 'points')


class TextQuestionOptionSerializer(ModelSerializer):
    """ """
    class Meta:
        model = TextQuestionOption
        fields = ('id', 'value', 'question')


class GeneralAnswerSerializer(ModelSerializer):
    """ """

    class Meta:
        model = GeneralAnswer
        fields = ('id', 'answer', 'positive_answer_value')


class OpenAnswerSerializer(ModelSerializer):
    """ """
    class Meta:
        model = OpenAnswer
        fields = ('id', 'answer')


class IntChoicesAnswerSerializer(ModelSerializer):
    """"""
    answer = PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = IntegerChoicesAnswer
        fields = ('id', 'answer')


class TextChoicesAnswerSerializer(ModelSerializer):
    """ """
    answer = PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = TextChoicesAnswer
        fields = ('id', 'answer')


class QuestionSerializer(ModelSerializer):
    """  """
    answer = SerializerMethodField()
    options = SerializerMethodField()

    def get_answer(self, instance):
        """ """
        answer = instance.answer
        if instance.type == QUESTION_TYPES['GENERAL']:
            return GeneralAnswerSerializer(answer).data
        elif instance.type == QUESTION_TYPES['OPEN']:
            return OpenAnswerSerializer(answer).data
        elif instance.type == QUESTION_TYPES['INT_CHOICES']:
            return IntChoicesAnswerSerializer(answer).data
        elif instance.type == QUESTION_TYPES['TEXT_CHOICES']:
            return TextChoicesAnswerSerializer(answer).data

    def get_options(self, instance):
        """ """
        if instance.type == QUESTION_TYPES['INT_CHOICES']:
            options = instance.int_options.all()
            return IntegerQuestionOptionSerializer(options, many=True).data
        elif instance.type == QUESTION_TYPES['TEXT_CHOICES']:
            options = instance.text_options.all()
            return TextQuestionOptionSerializer(options, many=True).data
        else:
            return {}

    class Meta:
        model = Question
        fields = ('id', 'section', 'text', 'type', 'answer', 'options')


class SubsectionSerializer(ModelSerializer):
    """ """
    questions = QuestionSerializer(many=True, read_only=True)
    name = SlugRelatedField(read_only=True, slug_field='value')

    class Meta:
        model = Section
        fields = ('id', 'name', 'parent', 'questions')


class SectionSerializer(ModelSerializer):
    """  """
    questions = QuestionSerializer(many=True, read_only=True)
    name = SlugRelatedField(read_only=True, slug_field='value')
    parent = PrimaryKeyRelatedField(read_only=True)
    subsections = SubsectionSerializer(many=True, read_only=True)

    class Meta:
        model = Section
        fields = ('id', 'name', 'parent', 'questions', 'subsections')


class ChecklistSerializer(ModelSerializer):
    """ """
    sections = SerializerMethodField()

    class Meta:
        model = Checklist
        fields = ('id', 'name', 'sections')

    def get_sections(self, instance):
        return SectionSerializer(Section.objects.filter(checklist_id=instance.id, parent=None), many=True).data
