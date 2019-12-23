from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http import FileResponse
from django.shortcuts import HttpResponse, get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views import generic
from django_filters.views import FilterView

from ghost_shopper.auth.decorators import staff_member_required
from ghost_shopper.checklist.file_generator import ChecklistToExcelConverter
from ghost_shopper.checklist.validator import ChecklistValidator
from ghost_shopper.user_profile.models import User
from ghost_shopper.user_profile.performer_filterset import PerformerFilterSet

from .enums import CheckStatusesEnum
from .filters import CheckFilterSet
from .forms import (CheckForm, CheckPerformerAppointForm, InvitePerformersForm,
                    PerformRequestForm)
from .models import Check, CheckPerformRequest


@method_decorator(staff_member_required, name='dispatch')
class ChecksListView(LoginRequiredMixin, FilterView):
    """List all usual(not check templates used in projects) checks."""

    queryset = Check.usual.all()
    filterset_class = CheckFilterSet
    login_url = reverse_lazy('auth:login')
    template_name = 'check/list.html'
    context_object_name = 'checks'
    paginate_by = 20


class AvailableChecksListView(LoginRequiredMixin, UserPassesTestMixin, generic.ListView):
    """List available checks.

    Shows checks with CheckStatusesEnum.AVAILABLE status only. Used by performers.
    """

    queryset = Check.usual.filter(status=CheckStatusesEnum.AVAILABLE)
    login_url = reverse_lazy('auth:login')
    template_name = 'check/available.html'
    context_object_name = 'checks'
    paginate_by = 20

    def test_func(self):
        """Show view only for performer and staff users."""
        return self.request.user.is_performer or self.request.user.is_staff

    def get_context_data(self, *, object_list=None, **kwargs):
        """Add data to page context."""
        context = super().get_context_data(object_list=object_list, **kwargs)
        context['page_title'] = 'Доступные проверки'
        return context


class PerformerClosedChecksListView(LoginRequiredMixin, UserPassesTestMixin, generic.ListView):
    """List closed checks for current performer."""

    template_name = 'check/available.html'
    filterset_class = CheckFilterSet
    login_url = reverse_lazy('auth:login')
    context_object_name = 'checks'

    def test_func(self):
        """Test that request user is performer of closed check(page user) or staff."""
        if self.request.user.is_staff:
            return True
        if self.request.user.is_performer:
            page_user = get_object_or_404(User, id=self.kwargs.get('pk', None))
            return page_user == self.request.user
        return False

    def get_queryset(self):
        """Get closed checks for given user."""
        performer = get_object_or_404(User, id=self.kwargs.get('pk', None))
        return Check.objects.filter(performer=performer, status=CheckStatusesEnum.CLOSED)

    def get_context_data(self, *, object_list=None, **kwargs):
        """Add data to page context."""
        context = super().get_context_data(object_list=object_list, **kwargs)
        context['page_title'] = 'Закрытые проверки'
        return context


class PerformerCurrentChecksListView(LoginRequiredMixin, UserPassesTestMixin, generic.ListView):
    """List current checks for given performer."""

    template_name = 'check/available.html'
    filterset_class = CheckFilterSet
    login_url = reverse_lazy('auth:login')
    context_object_name = 'checks'

    def test_func(self):
        """Test that request user is either staff user or checks performer."""
        if self.request.user.is_staff:
            return True
        if self.request.user.is_performer:
            page_user = get_object_or_404(User, id=self.kwargs.get('pk', None))
            return page_user == self.request.user
        return False

    def get_queryset(self):
        """Get current checks for given performer."""
        performer = get_object_or_404(User, id=self.kwargs.get('pk', None))
        return Check.objects.filter(performer=performer).exclude(status=CheckStatusesEnum.CLOSED)

    def get_context_data(self, *, object_list=None, **kwargs):
        """Add data to page context."""
        context = super().get_context_data(object_list=object_list, **kwargs)
        context['page_title'] = 'Текущие проверки'
        return context


@method_decorator(staff_member_required, name='dispatch')
class CheckCreateView(LoginRequiredMixin, generic.CreateView):
    """Check create view."""

    model = Check
    form_class = CheckForm
    login_url = reverse_lazy('auth:login')
    template_name = 'check/create.html'

    def form_valid(self, form):
        """Redirect user to new created check if form is valid."""
        check = form.save()
        return redirect(check.get_absolute_url())

    def get_context_data(self, **kwargs):
        """Add data to page context."""
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Создать проверку'
        return context


class CheckDetailView(LoginRequiredMixin, UserPassesTestMixin, generic.DetailView):
    """Check detail view."""

    queryset = Check.usual.all()
    template_name = 'check/detail.html'
    login_url = reverse_lazy('auth:login')
    context_object_name = 'check'

    def test_func(self):
        """Test if current request user can access this view."""
        current_check = get_object_or_404(Check, id=self.kwargs.get('pk', None))

        if self.request.user.is_performer:
            if current_check.status == CheckStatusesEnum.AVAILABLE and not (
                    current_check.performer and current_check.performer_typed):
                return True

            return self.request.user == current_check.performer

        elif self.request.user.is_customer:
            customer_organisation = self.request.user.profile.organisation_tree_node
            return current_check.target_id in customer_organisation.get_descendants_ids()

        elif self.request.user.is_staff:
            if self.request.user.is_superuser:
                return True
            else:
                return self.request.user == current_check.curator

        return False

    def get_context_data(self, **kwargs):
        """Add data to page context."""
        context = super().get_context_data(**kwargs)
        context['statuses'] = CheckStatusesEnum.values
        if self.request.user.is_performer:
            context['perform_request_form'] = PerformRequestForm(
                check_id=self.object.id, performer_id=self.request.user.id)
            context['perform_request_exists'] = self.request.user.perform_requests.filter(check_obj=self.object).exists()
        return context


class CheckUpdateView(LoginRequiredMixin, UserPassesTestMixin, generic.UpdateView):
    """Check update view"""

    queryset = Check.usual.all()
    form_class = CheckForm
    template_name = 'check/create.html'
    login_url = reverse_lazy('auth:login')

    def test_func(self):
        """Test that current user has access to this view"""
        current_check = get_object_or_404(Check, id=self.kwargs.get('pk', None))
        if self.request.user.is_staff:
            if self.request.user.is_superuser:
                return True
            else:
                return self.request.user == current_check.curator
        return False

    def get_context_data(self, **kwargs):
        """Add data to page context."""
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Редактировать проверку'
        return context


class CheckDeleteView(LoginRequiredMixin, UserPassesTestMixin, generic.DeleteView):
    """Check delete view"""

    queryset = Check.usual.all()
    template_name = 'base/confirm_delete.html'
    success_url = reverse_lazy('check:list')
    login_url = reverse_lazy('auth:login')

    def test_func(self):
        """Test that request user can access this view."""
        current_check = get_object_or_404(Check, id=self.kwargs.get('pk', None))

        if self.request.user.is_staff:

            if self.request.user.is_superuser:
                return True
            else:
                return self.request.user == current_check.curator
        else:
            return False


@method_decorator(staff_member_required, name='dispatch')
class CheckFileGenerateView(LoginRequiredMixin, generic.View):
    """Generates excel file for checklist related to this check."""

    def get(self, request, *args, **kwargs):
        """Generate new checklist file return it via response."""

        check = get_object_or_404(Check, id=kwargs.get('pk', None))
        checklist = check.checklist

        converter = ChecklistToExcelConverter(checklist=checklist)
        wb = converter.convert()

        response = HttpResponse(
            content=wb, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = 'attachment; filename={}'.format(converter.file_name)
        return response


class CheckMakeAvailableView(LoginRequiredMixin, UserPassesTestMixin, generic.View):
    """Make check available view."""

    login_url = reverse_lazy('auth:login')

    def test_func(self):
        """Test that request user can access this view."""
        current_check = get_object_or_404(Check, id=self.kwargs.get('pk', None))

        if self.request.user.is_staff:
            if self.request.user.is_superuser:
                return True
            else:
                return self.request.user == current_check.curator

        return False

    def post(self, request, *args, **kwargs):
        """Change check status to available."""
        check = get_object_or_404(Check.usual.all(), id=self.kwargs.get('pk', None))
        check.make_available()
        return redirect(check.get_absolute_url())


class CheckMakeProcessingView(LoginRequiredMixin, UserPassesTestMixin, generic.View):
    """Make check processing view."""

    login_url = reverse_lazy('auth:login')

    def test_func(self):
        """Test that request user can access this view."""
        current_check = get_object_or_404(Check, id=self.kwargs.get('pk', None))
        if self.request.user.is_staff:
            if self.request.user.is_superuser:
                return True
            else:
                return self.request.user == current_check.curator
        return False

    def post(self, request, *args, **kwargs):
        """Change check status to processing."""
        check = get_object_or_404(Check.usual.all(), id=self.kwargs.get('pk', None))
        check.make_processing()
        return redirect(check.get_absolute_url())


class CheckMakeFilledView(LoginRequiredMixin, UserPassesTestMixin, generic.View):
    """Make check filled view."""

    login_url = reverse_lazy('auth:login')

    def test_func(self):
        """Test that request user can access this view."""
        user = self.request.user
        check = get_object_or_404(Check, id=self.kwargs.get('pk', None))

        if user.is_staff:
            if user.is_superuser:
                return True
            else:
                return user == check.curator
        elif user.is_performer:
            return user == check.performer

        return False

    def post(self, request, *args, **kwargs):
        """Validate checklist related to check and change status to filled."""
        check = get_object_or_404(Check.usual.all(), id=self.kwargs.get('pk', None))
        validator = ChecklistValidator(check.checklist)
        if not validator.check_is_valid():
            self.request.session['checklist_is_valid'] = False
            self.request.session['error_message'] = validator.error_message
            return redirect(reverse_lazy('checklist:update', args=(check.checklist.id,)))
        check.make_filled()
        return redirect(check.get_absolute_url())


class CheckSendForReworkView(LoginRequiredMixin, UserPassesTestMixin, generic.View):
    """Send check for rework view."""

    login_url = reverse_lazy('auth:login')

    def test_func(self):
        """Test that request user can access this view."""
        current_check = get_object_or_404(Check, id=self.kwargs.get('pk', None))

        if self.request.user.is_staff:
            if self.request.user.is_superuser:
                return True
            else:
                return self.request.user == current_check.curator
        return False

    def post(self, request, *args, **kwargs):
        """Change check status to processing."""
        check = get_object_or_404(Check.usual.all(), id=self.kwargs.get('pk', None))
        check.send_for_rework()
        return redirect(check.get_absolute_url())


class CheckSendForCustomerConformationView(LoginRequiredMixin, UserPassesTestMixin, generic.View):
    """Send check to customer conformation view."""

    login_url = reverse_lazy('auth:login')

    def test_func(self):
        """Test that request user can access this view."""
        current_check = get_object_or_404(Check, id=self.kwargs.get('pk', None))

        if self.request.user.is_staff:
            if self.request.user.is_superuser:
                return True
            else:
                return self.request.user == current_check.curator
        return False

    def post(self, request, *args, **kwargs):
        """Change check status to conformation."""
        check = get_object_or_404(Check.usual.all(), id=self.kwargs.get('pk', None))
        check.send_for_conformation()
        return redirect(check.get_absolute_url())


class CheckCloseView(LoginRequiredMixin, UserPassesTestMixin, generic.View):
    """Close check view."""

    login_url = reverse_lazy('auth:login')

    def test_func(self):
        """Test that request user can access this view."""
        current_check = get_object_or_404(Check, id=self.kwargs.get('pk', None))

        if self.request.user.is_staff:
            if self.request.user.is_superuser:
                return True
            else:
                return self.request.user == current_check.curator
        return False

    def post(self, request, *args, **kwargs):
        """Change check status to close."""
        check = get_object_or_404(Check.usual.all(), id=self.kwargs.get('pk', None))
        check.close()
        return redirect(check.get_absolute_url())


class CheckPerformRequestCreateView(LoginRequiredMixin, UserPassesTestMixin, generic.View):
    """Create check perform request view."""

    login_url = reverse_lazy('auth:login')

    def test_func(self):
        """Test that request user can access this view."""
        if self.request.user.is_performer:
            return True
        return False

    def post(self, request, *args, **kwargs):
        """Validate form and redirect to check detail page."""
        form = PerformRequestForm(data=request.POST)
        if form.is_valid():
            perform_request = form.save()
            return redirect(reverse_lazy('check:detail', args=(perform_request.check_obj_id, )))
        else:
            check = get_object_or_404(Check.usual.all(), id=self.kwargs.get('pk', None))
            return redirect(check.get_absolute_url())


@method_decorator(staff_member_required, name='dispatch')
class CheckPerformRequestApproveView(LoginRequiredMixin, generic.View):
    """Approve perform request. """

    login_url = reverse_lazy('auth:login')

    def post(self, request, *args, **kwargs):
        """Approve perform requets."""
        perform_request = get_object_or_404(CheckPerformRequest, id=self.kwargs.get('pk', None))
        check = perform_request.check_obj
        perform_request.approve()
        return redirect(check.get_absolute_url())


@method_decorator(staff_member_required, name='dispatch')
class CheckAppointPerformerView(LoginRequiredMixin, generic.View):
    """Appoint performer for this check."""

    template_name = 'check/performer_appoint.html'
    login_url = reverse_lazy('auth:login')

    def get(self, request, *args, **kwargs):
        check = get_object_or_404(Check.usual.all(), id=kwargs.get('pk', None))

        performer_filterset = PerformerFilterSet(
            queryset=User.objects.filter(is_performer=True, performer_profile__is_approved=True),
            get_parameters=request.GET)

        context = {
            'form': CheckPerformerAppointForm(instance=check, prefix='choose'),
            'filter': performer_filterset,
            'invite_form': InvitePerformersForm(prefix='invite', performers_qs=performer_filterset.qs, check=check),
            'check': check}

        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):

        check = get_object_or_404(Check.usual.all(), id=self.kwargs.get('pk', None))
        context = {'check': check}
        form = CheckPerformerAppointForm(instance=check, data=request.POST, prefix='choose')
        invitation_form = InvitePerformersForm(
            data=request.POST,
            prefix='invite',
            performers_qs=User.objects.filter(is_performer=True, performer_profile__is_approved=True))

        if form.is_valid() and form.cleaned_data['performer'] is not None:
            check = form.save()
            return redirect(check.get_absolute_url())
        else:
            context['form'] = form

        if invitation_form.is_valid() and invitation_form.cleaned_data['performers']:
            invitation_form.save()
            return redirect(check.get_absolute_url())
        else:
            context['invite_form'] = invitation_form

        context['filter'] = PerformerFilterSet(
            queryset=User.objects.filter(is_performer=True, performer_profile__is_approved=True),
            get_parameters=request.GET)

        return render(request, self.template_name, context)
