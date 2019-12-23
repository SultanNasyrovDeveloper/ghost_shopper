from ghost_shopper.user_profile.models import User

from .models import News


class EventHandler:

    body_template = None

    def __init__(self, *args, **kwargs):
        self.check = kwargs.get('check')

    def handle(self):
        return NotImplementedError


class CheckCreatedEventHandler(EventHandler):
    """ """

    body_template = '''Создана новая проверка: <a href="">{}</a> {}'''

    def handle(self):
        news_body = self.body_template.format(self.check.get_absolute_url(), self.check.title, self.check.target.get_address())
        news_obj = News.objects.create(body=news_body)

        self.check.curator.news_feed.news.add(news_obj)
        superusers = User.objects.filter(is_superuser=True)
        for user in superusers:
            user.news_feed.news.add(news_obj)


class CheckAvailableEventHandler(EventHandler):
    """ """
    body_template1 = '''Проводится проверка <a href="{}">{}</a> {}'''
    body_template2 = '''Доступна новая проверка: <a href="{}">{}</a> {}'''

    def handle(self):
        news_body1 = self.body_template1.format(
            self.check.get_absolute_url(), self.check.title, self.check.target.get_address())
        news_obj1 = News.objects.create(body=news_body1)

        news_body2 = self.body_template2.format(
            self.check.get_absolute_url(), self.check.title, self.check.target.get_address())
        news_obj2 = News.objects.create(body=news_body2)

        self.check.curator.news_feed.news.add(news_obj1)
        superusers = User.objects.filter(is_superuser=True)
        for user in superusers:
            user.news_feed.news.add(news_obj1)


class CheckProcessingEventHandler(EventHandler):

    body_template = '''Проверка переведена в статус "В работе" <a href="{}">{}</a> с исполниетелем {}'''

    def __init__(self, check, performer):
        super().__init__(check=check)
        self.performer_name = performer

    def handle(self):

        news_body = self.body_template.format(
            self.check.get_absolute_url(), self.check.title, self.check.target.get_address(), self.performer_name)
        news_obj = News.objects.create(body=news_body)

        self.check.curator.news_feed.news.add(news_obj)
        superusers = User.objects.filter(is_superuser=True)
        for user in superusers:
            user.news_feed.news.add(news_obj)


class CheckFilledEventHandler(EventHandler):

    body_template1 = '''Проверка <a href="{}">{}</a> отправлена на анализ корректору'''
    body_template2 = '''Проверка <a href="{}">{}</a> требует анализа'''

    def handle(self):
        news_body1 = self.body_template1.format(self.check.get_absolute_url(), self.check.title)
        news_body2 = self.body_template2.format(self.check.get_absolute_url(), self.check.title)

        news_obj1 = News.objects.create(body=news_body1)
        news_obj2 = News.objects.create(body=news_body2)

        self.check.curator.news_feed.news.add(news_obj2)
        superusers = User.objects.filter(is_superuser=True)
        for user in superusers:
            user.news_feed.news.add(news_obj1)


class CheckSentToReworkEventHandler(EventHandler):

    body_template = '''Проверка <a href="{}">{}</a> отправлена на доработку тайному покупателю'''

    def handle(self):
        news_body = self.body_template.format(self.check.get_absolute_url(), self.check.title)
        news_obj = News.objects.create(body=news_body)

        self.check.curator.news_feed.news.add(news_obj)
        superusers = User.objects.filter(is_superuser=True)
        for user in superusers:
            user.news_feed.news.add(news_obj)


class CheckSentForConformation(EventHandler):
    body_template = """Проверка <a href="{}">{}</a> отравлена заказчику на одобрение"""

    def handle(self):
        news_body = self.body_template.format(self.check.get_absolute_url(), self.check.title)
        news_obj = News.objects.create(body=news_body)

        self.check.curator.news_feed.news.add(news_obj)
        superusers = User.objects.filter(is_superuser=True)
        for user in superusers:
            user.news_feed.news.add(news_obj)

        ancestor_nodes = self.check.target.get_ancestors(include_self=True)
        for node in ancestor_nodes:
            [employee_profile.user.news_feed.news.add(news_obj) for employee_profile in node.employee_profiles.all()]


class CheckAppealedEventHandler(EventHandler):
    body_template = '''Подана апелляция: <a href="{}">{}</a>'''

    def handle(self):
        news_body = self.body_template.format(self.check.get_absolute_url(), self.check.title)
        news_obj = News.objects.create(body=news_body)

        self.check.curator.news_feed.news.add(news_obj)
        superusers = User.objects.filter(is_superuser=True)
        for user in superusers:
            user.news_feed.news.add(news_obj)

        # TODO что имел ввиду когда говорил что должны получить оповещение все руководители подразделений
        ancestor_nodes = self.check.target.get_ancestors(include_self=True)
        for node in ancestor_nodes:
            [employee_profile.user.news_feed.add(news_obj) for employee_profile in node.employee_profiles.all()]


class CheckClosedEventHandler(EventHandler):
    body_template = '''Проверка закрыта: <a href="{}">{}</a>'''

    def handle(self):
        news_body = self.body_template.format(self.check.get_absolute_url(), self.check.title)
        news_obj = News.objects.create(body=news_body)

        self.check.curator.news_feed.news.add(news_obj)
        superusers = User.objects.filter(is_superuser=True)
        for user in superusers:
            user.news_feed.news.add(news_obj)

        # TODO что имел ввиду когда говорил что должны получить оповещение все руководители подразделений
        ancestor_nodes = self.check.target.get_ancestors(include_self=True)
        for node in ancestor_nodes:
            [employee_profile.user.news_feed.news.add(news_obj) for employee_profile in node.employee_profiles.all()]


