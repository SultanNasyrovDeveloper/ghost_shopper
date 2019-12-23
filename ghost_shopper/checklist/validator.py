from . import models
from .enums import QUESTION_TYPES


class ChecklistValidator:
    """Checklist validator.

    Class check whether given checklist has audio file assotiated with it and all questions are answered.
    """

    def __init__(self, checklist):
        """Initialize class."""
        self.checklist = checklist
        self._is_valid = True
        self._checked = False
        self._audio_is_valid = True
        self._audio_error_message = 'Прикрепите запись проверки(аудиофайл). '
        self._questions_are_valid = True
        self._questions_error_message = 'Ответьте на все вопросы.'

    @property
    def error_message(self):
        """Error messages."""
        message = ''
        if not self._audio_is_valid:
            message += self._audio_error_message

        if not self._questions_are_valid:
            message += self._questions_error_message
        return message

    def check_is_valid(self):
        """Return True if check is valid and False if not."""
        if not self._checked:
            self._validate()
        return self._is_valid

    def _validate(self):
        """Validate given check instance."""
        self._validate_audio()
        self._validate_all_questions()
        if not self._questions_are_valid or not self._audio_is_valid:
            self._is_valid = False

    def _get_all_question(self):
        """Get queryset with all questions in the check."""
        checklist_sections_ids = list(
            models.Section.objects.filter(checklist_id=self.checklist.id).values_list('id', flat=True)
        )
        questions = models.Question.objects.filter(section_id__in=checklist_sections_ids)
        return questions

    def _validate_all_questions(self):
        """Validate that all question are answered."""
        for question in self._get_all_question():
            if not question.is_answered:
                if self._questions_are_valid:
                    self._questions_are_valid = False

    def _validate_audio(self):
        """Validate that check has audio file related to it."""
        try:
            self.checklist.audio.file
        except ValueError:
            self._audio_is_valid = False
