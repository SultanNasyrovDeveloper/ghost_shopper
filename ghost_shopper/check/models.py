from datetime import date, datetime

from django.conf import settings
from django.contrib.sites.models import Site
from django.core.exceptions import ValidationError
from django.core.mail import EmailMessage
from django.db import models
from django.urls import reverse

from ghost_shopper.core.models import PerformerLettersTemplates
from ghost_shopper.news import event_handlers

from .enums import CHECK_TYPES, CheckStatusesEnum


class UsualChecksManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(type=CHECK_TYPES['USUAL'])


class Check(models.Model):
    """
    Check object.
    """
    project = models.OneToOneField('project.Project', on_delete=models.SET_NULL, null=True, blank=True,
                                related_name='check_obj', verbose_name='Проект')
    status = models.CharField(max_length=30, choices=tuple(CheckStatusesEnum.values.items()),
                              default=CheckStatusesEnum.CREATED, verbose_name='Статус')
    type = models.CharField(max_length=20, choices=tuple(CHECK_TYPES.items()), default=CHECK_TYPES['USUAL'],
                            verbose_name='Тип')
    kind = models.ForeignKey('core.CheckKind', on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Тип')
    start_date = models.DateField(null=True, blank=True, verbose_name='Дата начала')
    deadline = models.DateField(null=True, blank=True, verbose_name='Дедлайн')
    end_date = models.DateField(null=True, blank=True, verbose_name='Окончание')
    target = models.ForeignKey(
        'organisation_tree.OrganisationTreeNode',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name='Цель'
    )
    instruction = models.ForeignKey(
        'instruction.Instruction', on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Инструкция')
    performer = models.ForeignKey(
        'user_profile.User', on_delete=models.SET_NULL, null=True, blank=True, related_name='performer',
        verbose_name='Исполнитель')
    curator = models.ForeignKey(
        'user_profile.User', on_delete=models.SET_NULL, null=True, blank=True, related_name='checks',
        verbose_name='Куратор')
    reward = models.PositiveSmallIntegerField(default=0, verbose_name='Награда(руб.)')
    was_sent_to_rework = models.BooleanField(default=False, verbose_name='Была отправлена на доработку')
    was_appealed = models.BooleanField(default=False, verbose_name='Была аппеляция')
    conformation_period = models.PositiveSmallIntegerField('Дней на аппеляцию', default=1)
    comment = models.TextField(blank=True, null=True, verbose_name='Комментарий')

    sent_for_conformation_date = models.DateField(null=True, blank=True)

    objects = models.Manager()
    usual = UsualChecksManager()

    class Meta:
        ordering = ('start_date', )
        verbose_name = 'Проверка'
        verbose_name_plural = 'Проверки'

    @property
    def title(self):
        return self.__str__()

    def __str__(self):
        name = self.target.title if self.target else self.id
        return 'Проверка {}'.format(name)

    def get_absolute_url(self):
        return reverse('check:detail', args=(self.id,))

    def clone(self, new_target=None) -> None:
        """
        Clone this check.
        Returns:
            new_check (Check): new cloned check object.
        """
        instruction = self.instruction
        checklist = self.checklist

        new_check = self
        new_check.id = None
        new_check.project = None
        new_check.target = new_target
        new_check.status = CheckStatusesEnum.AVAILABLE
        new_check.type = CHECK_TYPES['USUAL']
        new_check.instruction = instruction
        new_check.save()
        new_check.checklist.delete()

        checklist.clone(new_check)
        return new_check

    def make_available(self):
        self.status = CheckStatusesEnum.AVAILABLE
        self.save()
        event_handler = event_handlers.CheckAvailableEventHandler(check=self)
        event_handler.handle()

    def make_processing(self):
        self.status = CheckStatusesEnum.PROCESSING
        self.save()
        self.perform_requests.all().delete()
        performer_name = self.performer.get_full_name() if self.performer else self.performer_typed
        event_handler = event_handlers.CheckProcessingEventHandler(self, performer_name)
        event_handler.handle()

    def make_filled(self):
        self.status = CheckStatusesEnum.FILLED
        self.save()
        event_handler = event_handlers.CheckFilledEventHandler(check=self)
        event_handler.handle()

    def send_for_rework(self):
        self.status = CheckStatusesEnum.PROCESSING
        self.was_sent_to_rework = True
        self.save()
        event_handler = event_handlers.CheckSentToReworkEventHandler(check=self)
        event_handler.handle()

    def send_for_conformation(self):
        self.status = CheckStatusesEnum.CONFORMATION
        self.sent_for_conformation_date = date.today()
        self.save()
        event_handler = event_handlers.CheckSentForConformation(check=self)
        event_handler.handle()

    def appeal(self):
        self.status = CheckStatusesEnum.APPEAL
        self.was_appealed = True
        self.save()
        event_handler = event_handlers.CheckAppealedEventHandler(check=self)
        event_handler.handle()

    def close(self):
        self.status = CheckStatusesEnum.CLOSED
        self.end_date = datetime.now()
        self.save()
        event_handler = event_handlers.CheckClosedEventHandler(check=self)
        event_handler.handle()


class CheckPerformRequest(models.Model):
    """
    Perform request for check.

    """
    check_obj = models.ForeignKey(Check, on_delete=models.CASCADE, related_name='perform_requests')
    performer = models.ForeignKey('user_profile.User', on_delete=models.CASCADE, related_name='perform_requests')

    class Meta:
        unique_together = ('check_obj', 'performer')

    def approve(self):
        self.check_obj.performer = self.performer
        self.check_obj.status = CheckStatusesEnum.PROCESSING
        self.check_obj.save()
        self.check_obj.perform_requests.all().delete()
        event_handler = event_handlers.CheckProcessingEventHandler(
            check=self.check_obj, performer=self.performer.get_full_name())
        event_handler.handle()
        self._inform_performer()
        self.delete()

    def save(self, *args, **kwargs):
        if not self.performer.is_performer:
            raise ValidationError('Исполнителем должен быть тайный покупатель, сейчас {}'.format(self.performer.status))
        return super().save(*args, **kwargs)

    def _inform_performer(self) -> None:
        """
        Inform performer that his/her perform request was approved.
        """
        site = Site.objects.get_current()
        letter_templates = PerformerLettersTemplates.get()
        subject = letter_templates.apply_subject

        try:
            message = letter_templates.apply_message.format(
                performer=self.performer.get_full_name(),
                check=self.check_obj.title,
                link='https://{}{}'.format(site.domain, self.check_obj.get_absolute_url())
            )
        except Exception:
            message = letter_templates.apply_subject.format(
                performer=self.performer.get_full_name(),
                check=self.check_obj.title,
                link='https://{}{}'.format(site.domain, self.check_obj.get_absolute_url())
            )
        email = EmailMessage(
            subject=subject,
            body=message,
            to=(self.performer.email,)
        )
        email.send()


class CheckPerformInvitation(models.Model):
    """
    Invitation to be performer of this check.
    """
    check_obj = models.ForeignKey(Check, on_delete=models.CASCADE, related_name='perform_invitations')
    performer = models.ForeignKey('user_profile.User', on_delete=models.CASCADE, related_name='perform_invitations')

    class Meta:
        unique_together = ('check_obj', 'performer')

    @classmethod
    def invite(cls, performer, check) -> None:
        """
        Invite performer to given check.

        Creates new invitation class with given parameters and sends an invitation email to performer.
        """
        invitation, created = cls.objects.get_or_create(check_obj=check, performer=performer)
        invitation._send_invitation_letter()

    def accept(self):
        """
        Accept this invitation and become the performer of the check.
        """
        self.check_obj.performer = self.performer
        self.check_obj.make_processing()
        self.delete()

    def _send_invitation_letter(self):
        """
        Send invitation to performer the check to the possible performer.
        """
        site = Site.objects.get_current()

        letter_templates = PerformerLettersTemplates.get()
        subject = letter_templates.invite_subject
        try:
            message = letter_templates.invite_message.format(
                performer=self.performer.get_full_name(),
                check=self.check_obj.title,
                link='https://{}{}'.format(site.domain, self.check_obj.get_absolute_url())
            )
        except Exception:
            message = letter_templates.default_invite.format(
                performer=self.performer.get_full_name(),
                check=self.check_obj.title,
                link='https://{}{}'.format(site.domain, self.check_obj.get_absolute_url())
            )

        email = EmailMessage(
            subject=subject,
            body=message,
            to=(self.performer.email, )
        )
        email.send()
