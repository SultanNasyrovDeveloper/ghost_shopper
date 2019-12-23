from . import models


class PerformerProfileValidator:

    field_names_map = {
        'avatar': 'фото',
        'first_name': 'имя',
        'last_name': 'фамилия',
        'patronymic': 'отчество',
        'phone_number': 'контактный номер',
        'birth_date': 'дата рождения',
        'city': 'город',
        'work_cities': 'города проведения проверок',
        'education': 'образование',
        'work_place': 'место работы',
        'position': 'должность',
        'transport': 'транспортные средства'
    }

    required_user_fields = ['avatar','first_name','last_name', 'phone_number']
    required_profile_fields = ['birth_date', 'city']

    def __init__(self, user):

        assert isinstance(user, models.User)
        assert user.is_performer

        self._is_valid = True
        self.checked = False
        self.user = user
        self.user_profile = user.profile
        self.error_message = 'Для отправки запроса на подтверждение заполните следующие поля: '

    @property
    def error_message_text(self):
        return self.error_message.strip(', ')

    @property
    def is_valid(self):
        if not self.checked:
            self.validate()
        return self._is_valid

    def validate(self):
        for field_name in self.required_user_fields:
            if getattr(self.user, field_name) is None:
                self._is_valid = False
                self._add_field_to_error_message(field_name)

        for field_name in self.required_profile_fields:
            if getattr(self.user_profile, field_name) is None:
                self._is_valid = False
                self._add_field_to_error_message(field_name)

        if not self.user_profile.autos.exists():
            self._is_valid = False
            self._add_field_to_error_message('transport')

        self.checked = True

    def _add_field_to_error_message(self, field_name):
        translated_field_name = self.field_names_map[field_name]
        field_name = translated_field_name + ', '
        self.error_message += field_name

