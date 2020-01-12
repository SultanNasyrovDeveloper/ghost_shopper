from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views import generic
from django.views.generic.edit import FormMixin, ProcessFormView
from django.contrib.auth.models import Group
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.utils.decorators import method_decorator
from django.forms.models import modelform_factory

from ghost_shopper.auth.decorators import staff_member_required

from ghost_shopper.checklist.models import SectionName

from . import models
from . import forms


@method_decorator(staff_member_required, name='dispatch')
class MyOrganisationUpdateView(LoginRequiredMixin, generic.UpdateView):
    """My organisation singleton class update view."""

    model = models.MyOrganisation
    form_class = forms.MyOrganisationForm
    template_name = 'core/my_organisation.html'
    login_url = reverse_lazy('auth:login')

    def get_success_url(self):
        """Get success url for the view."""
        return reverse_lazy('core:my-organisation')

    def get_object(self, queryset=None):
        """Get my organisation instance."""
        return models.MyOrganisation.get()


class CheckKindListView(LoginRequiredMixin, generic.ListView, FormMixin, ProcessFormView):
    """Check kind list and also create view."""

    model = models.CheckKind
    form_class = forms.CheckKindForm
    template_name = 'core/check-kind-list.html'
    context_object_name = 'check_kinds'
    paginate_by = 20
    login_url = reverse_lazy('auth:login')

    def form_valid(self, form):
        """Redirect user to self if form is valid."""
        form.save()
        return redirect(reverse_lazy('core:check-kind-list'))


class CheckKindUpdateView(LoginRequiredMixin, generic.UpdateView):
    """
    Update check kind.
    """
    model = models.CheckKind
    template_name = 'core/check_kind_update.html'
    context_object_name = 'check_kind'
    form_class = forms.CheckKindForm
    success_url = reverse_lazy('core:check-kind-list')
    login_url = reverse_lazy('auth:login')


@method_decorator(staff_member_required, name='dispatch')
class CheckKindDeleteView(LoginRequiredMixin, generic.DeleteView):
    """Check kind delete view."""

    model = models.CheckKind
    template_name = 'base/confirm_delete.html'
    success_url = reverse_lazy('core:check-kind-list')
    login_url = reverse_lazy('auth:login')


@method_decorator(staff_member_required, name='dispatch')
class SectionListView(LoginRequiredMixin, generic.ListView, FormMixin, ProcessFormView):
    """Section list view."""

    model = SectionName
    form_class = forms.SectionNameForm
    template_name = 'core/section_name_list.html'
    context_object_name = 'sections'
    paginate_by = 20
    login_url = reverse_lazy('auth:login')

    def form_valid(self, form):
        form.save()
        return redirect(reverse_lazy('core:section_name_list'))


@method_decorator(staff_member_required, name='dispatch')
class SectionUpdateView(LoginRequiredMixin, generic.UpdateView):

    model = SectionName
    template_name = 'core/section_name_update.html'
    context_object_name = 'section_name'
    form_class = forms.SectionNameForm
    success_url = reverse_lazy('core:section_name_list')
    login_url = reverse_lazy('auth:login')



@method_decorator(staff_member_required, name='dispatch')
class SectionDeleteView(LoginRequiredMixin, generic.DeleteView):

    model = SectionName
    template_name = 'base/confirm_delete.html'
    success_url = reverse_lazy('core:section_name_list')
    login_url = reverse_lazy('auth:login')


@method_decorator(staff_member_required, name='dispatch')
class CityListView(LoginRequiredMixin, generic.ListView, FormMixin, ProcessFormView):

    model = models.City
    form_class = forms.CityForm
    template_name = 'core/cities_list.html'
    context_object_name = 'cities'
    paginate_by = 20
    login_url = reverse_lazy('auth:login')

    def form_valid(self, form):
        form.save()
        return redirect(reverse_lazy('core:city-list'))


@method_decorator(staff_member_required, name='dispatch')
class CityDeleteView(LoginRequiredMixin, generic.DeleteView):

    model = models.City
    template_name = 'base/confirm_delete.html'
    success_url = reverse_lazy('core:city-list')
    login_url = reverse_lazy('auth:login')


@method_decorator(staff_member_required, name='dispatch')
class CarBrandListView(LoginRequiredMixin, generic.ListView, FormMixin, ProcessFormView):

    model = models.CarBrand
    form_class = forms.CarBrandForm
    template_name = 'core/car_brand_list.html'
    context_object_name = 'car_brands'
    paginate_by = 40
    login_url = reverse_lazy('auth:login')

    def form_valid(self, form):
        form.save()
        return redirect(reverse_lazy('core:car-brand-list'))


@method_decorator(staff_member_required, name='dispatch')
class CarBrandDeleteView(LoginRequiredMixin, generic.DeleteView):

    model = models.CarBrand
    template_name = 'base/confirm_delete.html'
    success_url = reverse_lazy('core:car-brand-list')
    login_url = reverse_lazy('auth:login')
    paginate_by = 20


@method_decorator(staff_member_required, name='dispatch')
class CarModelListView(LoginRequiredMixin, generic.ListView, FormMixin, ProcessFormView):

    model = models.CarModel
    form_class = forms.CarModelForm
    template_name = 'core/car-model-list.html'
    context_object_name = 'car_models'
    paginate_by = 20
    login_url = reverse_lazy('auth:login')

    def get_queryset(self):
        return models.CarModel.objects.filter(brand_id=self.kwargs.get('pk', None))

    def form_valid(self, form):
        model = form.save()
        return redirect(reverse_lazy('core:car-model-list', args=(model.brand_id, )))

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(object_list=object_list, **kwargs)
        context['form'].fields['brand'].initial = get_object_or_404(models.CarBrand, id=self.kwargs.get('pk', None))
        return context


@method_decorator(staff_member_required, name='dispatch')
class CarModelDeleteView(LoginRequiredMixin, generic.DeleteView):

    model = models.CarModel
    template_name = 'base/confirm_delete.html'
    login_url = reverse_lazy('auth:login')

    def get_success_url(self):
        return reverse_lazy('core:car-model-list', args=(self.object.brand_id, ))


class PerformerLettersTemplateUpdateView(generic.View):

    model = models.PerformerLettersTemplates
    template_name = 'core/templates.html'
    form_class = forms.PerformerInvitationLetterForm
    login_url = reverse_lazy('auth:login')

    def get_object(self):
        return models.PerformerLettersTemplates.get()

    def get(self, request, *args, **kwargs):
        context = {'form': self.form_class(instance=self.get_object())}

        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        form = self.form_class(instance=self.get_object(), data=request.POST)
        if form.is_valid():
            form.save()
            return redirect(reverse_lazy('core:performer-letters-template'))
        return render(request, self.template_name, {'form': form})

