from . import forms, models
from .enums import QUESTION_TYPES


def get_answer_form(question, answer, data):
    """ """
    map = {
        QUESTION_TYPES['GENERAL']: forms.GeneralAnswerForm,
        QUESTION_TYPES['OPEN']: forms.OpenAnswerForm,
        QUESTION_TYPES['INT_CHOICES']: forms.IntegerChoicesAnswerForm,
        QUESTION_TYPES['TEXT_CHOICES']: forms.TextChoicesAnswerForm
    }
    return map[question.type](instance=answer, prefix='form {}'.format(answer.id), data=data)


class ChecklistFormset:
    """
    Dict based checklist formset
    """
    def __init__(self, checklist_id, data=None):
        """ """
        self.formset = dict()
        self.checklist = models.Checklist.objects.get(id=checklist_id)

        for section in self.checklist.sections.filter(parent=None):
            self.formset[section.name.value] = {}
            section_dict = self.formset[section.name.value]
            section_dict['questions'] = {}
            questions = section_dict['questions']
            for question in section.questions.all():
                questions[question.text] = get_answer_form(question, question.answer, data)
            if section.subsections.exists():
                section_dict['subsections'] = {}
                subsections_dict = section_dict['subsections']
                for subsection in section.subsections.all():
                    subsections_dict[subsection.name.value] = {}
                    subsection_dict = subsections_dict[subsection.name.value]
                    for question in subsection.questions.all():
                        subsection_dict[question.text] = get_answer_form(question, question.answer, data)

    def is_valid(self):
        forms_is_valid = True
        for section in self.formset.values():
            for answer_form in section['questions'].values():
                if answer_form.is_valid():
                    continue
                else:
                    forms_is_valid = False

            if section.get('subsections', None):
                for subsection in section['subsections'].values():
                    if subsection:
                        for answer_form in subsection.values():
                            if answer_form.is_valid():
                                continue
                            else:
                                forms_is_valid = False
        return forms_is_valid

    def save(self):
        for section in self.formset.values():
            for answer_form in section['questions'].values():
                answer_form.save()
            if section.get('subsections', None):
                for subsection in section['subsections'].values():
                    for answer_form in subsection.values():
                        answer_form.save()
