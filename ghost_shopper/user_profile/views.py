from dal import autocomplete as ac
from django.core.paginator import Paginator
from django.urls import reverse_lazy
from django.db.models import Q
from django.views import generic
from django_filters.views import FilterView
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.utils.decorators import method_decorator

from ghost_shopper.auth.decorators import staff_member_required

from ghost_shopper.core.models import CarBrand, CarModel

from .enums import ApprovalRequestStatusesEnum
from .performer_profile_validator import PerformerProfileValidator
from .performer_filterset import PerformerFilterSet
from . import forms
from . import filters
from . import models


@method_decorator(staff_member_required, name='dispatch')
class UserCreateView(LoginRequiredMixin, generic.CreateView):

    login_url = reverse_lazy('auth:login')
    model = models.User
    template_name = 'profile/create.html'


@method_decorator(staff_member_required, name='dispatch')
class UserListView(LoginRequiredMixin, FilterView):

    model = models.User
    template_name = 'profile/list.html'
    login_url = reverse_lazy('auth:login')
    context_object_name = 'users'
    filterset_class = filters.UserSearch
    paginate_by = 20

    def get_context_data(self, *, object_list=None, **kwargs):
        """
        Add data to page context.
        """
        context = super().get_context_data(object_list=object_list, **kwargs)
        context['page_name'] = 'Список пользователей'
        return context


class PerformerListView(generic.TemplateView):

    template_name = 'profile/performers_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        filter = PerformerFilterSet(
            get_parameters=self.request.GET,
            queryset=models.User.objects.filter(is_performer=True)
        )
        context['filter'] = filter
        paginator = Paginator(filter.qs, 20)
        page = self.request.GET.get('page')
        context['users'] = paginator.get_page(page)
        context['page_name'] = 'Список пользователей'
        return context


class UserProfileDetail(LoginRequiredMixin, UserPassesTestMixin, generic.View):

    login_url = reverse_lazy('auth:login')

    def test_func(self):
        user = self.request.user
        profile_user = get_object_or_404(models.User, id=self.kwargs.get('pk', None))

        if user.is_performer:
            return user == profile_user
        elif user.is_customer:
            return user == profile_user or profile_user in user.profile.organisation_tree_node.get_employees()
        elif user.is_staff:
            return True
        else:
            return False

    def get(self, request, *args, **kwargs):

        user = get_object_or_404(models.User, id=kwargs.get('pk', None))
        context = dict()
        context['user_obj'] = user
        if user.is_performer:
            context['auto_form'] = forms.PerformerAutoForm(owner=user.id)
            context['approval_request_statuses'] = ApprovalRequestStatusesEnum
            context['validation_errors'] = self.get_validation_errors()
            if hasattr(user.profile, 'approve_request'):
                context['decline_form'] = forms.ApproveRequestDeclineForm(instance=user.profile.approve_request)
        return render(request, 'profile/detail.html', context)

    def post(self, request, *args, **kwargs):
        user = get_object_or_404(models.User, id=kwargs.get('pk', None))
        auto_form = forms.PerformerAutoForm(data=request.POST)
        if auto_form.is_valid():
            auto_form.save()
            return redirect(reverse_lazy('profile:detail', args=(user.id, )))
        else:
            context = {'user_obj': user, 'auto_form': auto_form}
            return render(request, 'profile/detail.html', context)

    def get_validation_errors(self):
        message = None
        if 'performer_validation_errors' in self.request.session:
            message = self.request.session['performer_validation_errors']
            self.request.session.pop('performer_validation_errors')
        print(message)
        return message


class ProfileUpdateView(LoginRequiredMixin, UserPassesTestMixin,  generic.View):

    login_url = reverse_lazy('auth:login')

    def test_func(self):
        user = self.request.user
        profile_user = get_object_or_404(models.User, id=self.kwargs.get('pk', None))

        if user.is_performer:
            return user == profile_user

        elif user.is_customer:
            return user == profile_user or profile_user in user.profile.organisation_tree_node.get_employees()

        elif user.is_staff:
            return True

    def get(self, request, *args, **kwargs):
        user = get_object_or_404(models.User, id=kwargs.get('pk', None))
        user_form = forms.UserForm(instance=user, prefix='user')
        if user.is_performer:
            profile_form = forms.PerformerProfileForm(instance=user.profile, prefix='profile')
            context = {'user_obj': user, 'user_form': user_form, 'profile_form': profile_form}
        else:
            context = {'user_obj': user, 'user_form': user_form}
        return render(request, 'profile/update.html', context)

    def post(self, request, *args, **kwargs):
        user = get_object_or_404(models.User, id=kwargs.get('pk', None))
        user_form = forms.UserForm(data=request.POST, instance=user, prefix='user', files=request.FILES)

        if user.is_performer:
            profile_form = forms.PerformerProfileForm(data=request.POST, instance=user.profile, prefix='profile')
            if user_form.is_valid() and profile_form.is_valid():
                user = user_form.save()
                profile_form.save()
                return redirect(reverse_lazy('profile:detail', args=(user.id, )))
            else:
                return render(request, 'profile/update.html', {
                    'user_form': user_form, 'profile_form': profile_form, 'user_obj': 'user'})
        else:
            if user_form.is_valid():
                user = user_form.save()
                return redirect(reverse_lazy('profile:detail', args=(user.id,)))
            else:
                return render(request, 'profile/update.html', {'user_form': user_form, 'user_obj': user})


@method_decorator(staff_member_required, name='dispatch')
class UserPermissionsUpdate(LoginRequiredMixin, generic.UpdateView):

    login_url = reverse_lazy('auth:login')

    model = models.User
    template_name = 'profile/permissions_update.html'
    form_class = forms.StaffPermissionsForm

    def get_success_url(self):
        return reverse_lazy('profile:detail', args=(self.object.id, ))


@method_decorator(staff_member_required, name='dispatch')
class UserDeleteView(LoginRequiredMixin, generic.DeleteView):

    model = models.User
    login_url = reverse_lazy('auth:login')
    template_name = 'base/confirm_delete.html'
    success_url = reverse_lazy('profile:list')


class PerformerAutoDeleteView(LoginRequiredMixin, generic.View):

    http_method_names = ('post', )

    def post(self, request, *args, **kwargs):
        auto = get_object_or_404(models.PerformerAuto, id=self.kwargs.get('pk', None))
        user = auto.performer_profile.user
        auto.delete()
        return redirect(user.get_absolute_url())


@method_decorator(staff_member_required, name='dispatch')
class PerformerApprovalRequestListView(LoginRequiredMixin, generic.ListView):
    queryset = models.PerformerApproveRequest.objects.filter(status=ApprovalRequestStatusesEnum.ACTIVE)
    template_name = 'profile/approve_requests_list.html'
    context_object_name = 'requests'
    paginate_by = 20


class PerformerApprovalRequestCreateView(LoginRequiredMixin, generic.View):

    login_url = reverse_lazy('auth:login')
    http_method_names = ('post', )

    def post(self, request, *args, **kwargs):
        user = get_object_or_404(models.User, id=self.kwargs.pop('pk', None))
        validator = PerformerProfileValidator(user)
        if validator.is_valid:
            if hasattr(user.profile, 'approve_request'):
                approve_request = user.profile.approve_request
                approve_request.status = ApprovalRequestStatusesEnum.ACTIVE
                approve_request.save()
            else:
                models.PerformerApproveRequest.objects.create(performer_profile=user.profile)
            return redirect(user.get_absolute_url())
        else:
            request.session['performer_validation_errors'] = validator.error_message_text
            return redirect(user.get_absolute_url())


@method_decorator(staff_member_required, name='dispatch')
class PerformerApprovalRequestDeclineView(LoginRequiredMixin, generic.View):

    def post(self, request, *args, **kwargs):
        user = get_object_or_404(models.User, id=self.kwargs.get('pk', None))
        form = forms.ApproveRequestDeclineForm(request.POST, instance=user.profile.approve_request)
        if form.is_valid():
            approve_request = form.save()
            approve_request.decline()
            return redirect(approve_request.performer_profile.user.get_absolute_url())


@method_decorator(staff_member_required, name='dispatch')
class PerformerApprovalRequestAcceptView(LoginRequiredMixin, generic.View):
    def post(self, request, *args, **kwargs):
        user = get_object_or_404(models.User, id=self.kwargs.get('pk', None))
        approval_request = user.profile.approve_request
        approval_request.approve()
        return redirect(user.get_absolute_url())


class UserAutocompleteView(LoginRequiredMixin, ac.Select2QuerySetView):

    login_url = reverse_lazy('auth:login')

    def get_queryset(self):
        queryset = models.User.objects.all()
        if self.q:
            queryset = queryset.filter(
                Q(first_name__icontains=self.q) | Q(last_name__icontains=self.q) | Q(patronymic__icontains=self.q)
                | Q(username__icontains=self.q) | Q(email__icontains=self.q)
            )
        return queryset

    def get_result_label(self, result):
        return result.get_full_name()

    def get_result_value(self, result):
        return result.id


class PerformerAutocompleteView(LoginRequiredMixin, ac.Select2QuerySetView):

    login_url = reverse_lazy('auth:login')

    def get_queryset(self):
        queryset = models.User.objects.filter(is_performer=True, performer_profile__is_approved=True)
        if self.q:
            queryset = queryset.filter(
                Q(first_name__icontains=self.q) | Q(last_name__icontains=self.q) | Q(patronymic__icontains=self.q)
                | Q(username__icontains=self.q) | Q(email__icontains=self.q)
            )
        return queryset

    def get_result_label(self, result):
        return result.get_full_name()

    def get_result_value(self, result):
        return result.id


class PerformerCarBrandAutocompleteView(LoginRequiredMixin, ac.Select2QuerySetView):
    def get_queryset(self):
        queryset = CarBrand.objects.all()
        if self.q:
            queryset = queryset.filter(name__icontains=self.q)
        return queryset

    def get_result_label(self, result):
        return result.name

    def get_result_value(self, result):
        return result.id


class PerformerCarModelAutocompleteView(ac.Select2QuerySetView):
    def get_queryset(self):
        queryset = CarModel.objects.all()
        brand = self.forwarded.get('brand', None)
        if brand:
            queryset = queryset.filter(brand_id=brand)
        if self.q:
            queryset.filter(name__icontains=self.q)
        return queryset

    def get_result_label(self, result):
        return result.name

    def get_result_value(self, result):
        return result.id




