from datetime import date

from dal import autocomplete as ac
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Q, QuerySet
from django.shortcuts import Http404, get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views import generic
from django_filters.views import FilterView

from ghost_shopper.auth.decorators import staff_member_required
from ghost_shopper.check.enums import CheckStatusesEnum
from ghost_shopper.check.filters import (
    OrganisationChecksFilterset, OrganisationClosedChecksFilterSet
)
from ghost_shopper.organisation_chat.forms import CommentForm, MessageForm
from ghost_shopper.organisation_tree.docs.manager import OrganisationsDocumentManager
from ghost_shopper.check.filters import ChecksForStatisticsFilterSet
from ghost_shopper.user_profile.forms import CustomerCreationForm

from . import filters, forms, models
from .statistics import ChecksStatisticsByOrganisation


@method_decorator(staff_member_required, name='dispatch')
class OrganisationListView(LoginRequiredMixin, FilterView):
    """
    Organisations list view.

    """

    template_name = 'organisation/list.html'
    queryset = models.OrganisationTreeNode.objects.filter(level=0)
    filterset_class = filters.OrganisationSearch
    context_object_name = 'organisations'
    paginate_by = 10
    login_url = reverse_lazy('auth:login')

    def get_context_data(self, *, object_list=None, **kwargs):
        """
        Add data to view context.
        """
        context = super().get_context_data(object_list=object_list, **kwargs)
        context['organisation_form'] = forms.OrganisationForm()
        return context


class OrganisationDetailView(LoginRequiredMixin, UserPassesTestMixin, FilterView):
    """
    Organisation detail view.

    """

    filterset_class = OrganisationChecksFilterset
    template_name = 'organisation/detail.html'
    context_object_name = 'checks'
    paginate_by = 5
    login_url = reverse_lazy('auth:login')

    def test_func(self):
        user = self.request.user
        organisation = get_object_or_404(models.OrganisationTreeNode, id=self.kwargs.get('pk', None))

        if user.is_customer:
            customer_organisation_ids = user.profile.organisation_tree_node.get_descendants_ids()
            return organisation.id in customer_organisation_ids

        elif user.is_staff:
            return True

        else:
            return False

    def get_queryset(self):
        organisation = get_object_or_404(models.OrganisationTreeNode, id=self.kwargs.get('pk', None))
        return organisation.get_checks()

    def get_context_data(self, *, object_list=None, **kwargs):

        context = super().get_context_data(object_list=object_list, **kwargs)
        organisation = get_object_or_404(models.OrganisationTreeNode, id=self.kwargs.get('pk'))
        context['organisation'] = organisation

        if organisation.level == 0:
            context['form'] = forms.LocationForm(parent=organisation)
        elif organisation.level == 1:
            context['form'] = forms.DepartmentForm(parent=organisation)

        context['message_form'] = MessageForm(chat=organisation.get_root().chat, author=self.request.user)
        context['comment_form'] = CommentForm(author=self.request.user)
        context['chat'] = organisation.get_root().chat
        return context

    def post(self, request, *args, **kwargs):
        self.object_list = self.get_queryset()
        self.object = get_object_or_404(models.OrganisationTreeNode, id=self.kwargs.get('pk', None))

        if self.object.level == 0:
            form = forms.LocationForm(parent=self.object, data=request.POST)
        elif self.object.level == 1:
            form = forms.DepartmentForm(parent=self.object, data=request.POST)

        if form.is_valid():
            form.save()
            return redirect(reverse_lazy('organisation:detail', args=(self.object.id, )))
        else:
            context = self.get_context_data()
            context['form'] = form
            return render(request, self.template_name, context)


@method_decorator(staff_member_required, name='dispatch')
class OrganisationCreateView(LoginRequiredMixin, generic.CreateView):
    model = models.OrganisationTreeNode
    form_class = forms.OrganisationForm
    http_method_names = ('post', )
    login_url = reverse_lazy('auth:login')


@method_decorator(staff_member_required, name='dispatch')
class OrganisationUpdateView(LoginRequiredMixin, generic.UpdateView):
    """ """
    queryset = models.OrganisationTreeNode.objects.filter()
    template_name = 'organisation/update.html'
    context_object_name = 'organisation'
    login_url = reverse_lazy('auth:login')

    def get_form_class(self):
        """
        Get form class for current instance of organisation node.
        """
        instance = self.get_object()

        if instance.level == 0:
            return forms.OrganisationForm
        elif instance.level == 1:
            return forms.LocationForm
        else:
            return forms.DepartmentUpdateForm

    def get_success_url(self):
        return reverse_lazy('organisation:detail', args=(self.get_object().id, ))

    def form_valid(self, form):
        instance = form.save()
        return redirect(reverse_lazy('organisation:detail', args=(instance.id, )))


@method_decorator(staff_member_required, name='dispatch')
class OrganisationDeleteView(LoginRequiredMixin, generic.DeleteView):
    model = models.OrganisationTreeNode
    template_name = 'base/confirm_delete.html'
    success_url = reverse_lazy('organisation:list')
    login_url = reverse_lazy('auth:login')


class OrganisationChecksListView(LoginRequiredMixin, UserPassesTestMixin, FilterView):

    template_name = 'organisation/checks.html'
    filterset_class = OrganisationClosedChecksFilterSet
    context_object_name = 'checks'
    paginate_by = 20
    login_url = reverse_lazy('auth:login')

    def test_func(self):
        user = self.request.user

        if user.is_customer:
            organisation_node = get_object_or_404(models.OrganisationTreeNode, id=self.kwargs.get('pk', None))
            user_organisation_ids = user.profile.organisation_tree_node.get_descendants_ids()
            return organisation_node.id in user_organisation_ids
        if user.is_staff:
            return True
        else:
            return False

    def get_queryset(self):
        organisation_node = get_object_or_404(models.OrganisationTreeNode, id=self.kwargs.get('pk', None))
        return organisation_node.get_checks()

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(object_list=object_list, **kwargs)
        organisation = get_object_or_404(models.OrganisationTreeNode, id=self.kwargs.get('pk', None))
        context['organisation_id'] = organisation.id
        return context


class OrganisationCurrentChecksListView(LoginRequiredMixin, UserPassesTestMixin, generic.ListView):
    template_name = 'organisation/current_checks.html'
    context_object_name = 'checks'
    paginate_by = 20
    login_url = reverse_lazy('auth:login')

    def test_func(self):
        user = self.request.user

        if user.is_customer:
            organisation_node = get_object_or_404(models.OrganisationTreeNode, id=self.kwargs.get('pk', None))
            user_organisation_ids = user.profile.organisation_tree_node.get_descendants_ids()
            return organisation_node.id in user_organisation_ids
        if user.is_staff:
            return True
        else:
            return False

    def get_queryset(self):
        organisation_node = get_object_or_404(models.OrganisationTreeNode, id=self.kwargs.get('pk', None))
        checks = organisation_node.get_current_checks()
        return checks


class OrganisationStatisticsView(LoginRequiredMixin, UserPassesTestMixin, FilterView):
    """
    Organisation statistics view.

    Filters queryset according to filter set and generates statistical data for given checks.
    """

    template_name = 'organisation/statistics.html'
    filterset_class = ChecksForStatisticsFilterSet
    login_url = reverse_lazy('auth:login')

    def test_func(self):
        user = self.request.user
        organisation = get_object_or_404(models.OrganisationTreeNode, id=self.kwargs.get('pk', None))

        if user.is_customer:
            customer_organisation_ids = user.profile.organisation_tree_node.get_descendants_ids()
            return organisation.id in customer_organisation_ids

        elif user.is_staff:
            return True

        else:
            return False

    def get(self, request, *args, **kwargs):
        """
        Get request processing.
        """
        organisation = get_object_or_404(models.OrganisationTreeNode, id=kwargs.get('pk', None))
        initial_checks = organisation.get_checks()
        filter = ChecksForStatisticsFilterSet(
            request.GET,
            initial_checks,
            nodes=organisation.get_descendants(include_self=True).exclude(level=0),
        )
        calculator = ChecksStatisticsByOrganisation(filter.qs)
        context = {'filter': filter, 'statistics': calculator.calculate(), 'organisation': organisation}
        return render(request, self.template_name, context)

@method_decorator(staff_member_required, name='dispatch')
class CreateEmployeeView(LoginRequiredMixin, generic.View):

    login_url = reverse_lazy('auth:login')

    def get(self, request, *args, **kwargs):
        context = {
            'form': CustomerCreationForm(organisation_id=kwargs.get('pk'))
        }
        return render(request, 'profile/create.html', context)

    def post(self, request, *args, **kwargs):
        form = CustomerCreationForm(request.POST, organisation_id=self.kwargs.get('pk'))
        if form.is_valid():
            form.save()
            return redirect(reverse_lazy('organisation:detail', args=(self.kwargs.get('pk'),)))
        else:
            context = {
                'form': form
            }
            return render(request, 'profile/create.html', context)



class OrganisationDocsListView(LoginRequiredMixin, UserPassesTestMixin, FilterView):
    """Organisation documents list view.
    Show list of document objects for given organisation.

    """
    model = models.OrganisationMonthlyDocumentStorage
    template_name = 'organisation/docs-list.html'
    filterset_class = filters.OrganisationDocumentFilter
    context_object_name = 'docs'
    paginate_by = 30

    def test_func(self):
        user = self.request.user
        organisation = get_object_or_404(models.OrganisationTreeNode, id=self.kwargs.get('pk', None))

        if user.is_customer:
            customer_organisation_ids = user.profile.organisation_tree_node.get_descendants_ids()
            return organisation.id in customer_organisation_ids

        elif user.is_staff:
            return True

        else:
            return False

    def get_queryset(self):
        """Get documents only for current organisation."""
        if self.kwargs.get('pk', None) is None:
            raise Http404
        docs = models.OrganisationMonthlyDocumentStorage.objects.filter(organisation_id=self.kwargs.get('pk', None))
        return docs

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(object_list=object_list, **kwargs)
        context['organisation'] = get_object_or_404(models.OrganisationTreeNode, id=self.kwargs.get('pk')).get_root()
        return context


class OrganisationDocsStorageDetailView(LoginRequiredMixin, generic.DetailView):
    """Organisation documents detail view.
    Show template with organisation documents download links.

    """
    model = models.OrganisationMonthlyDocumentStorage
    template_name = 'organisation/docs-detail.html'
    context_object_name = 'storage'


class OrganisationAutocompleteView(LoginRequiredMixin, ac.Select2QuerySetView):

    def get_queryset(self):
        queryset = models.OrganisationTreeNode.objects.filter(level=0)
        if self.q:
            queryset = queryset.filter(Q(name__icontains=self.q))
        return queryset

    def get_result_label(self, result):
        return result.title

    def get_result_value(self, result):
        return result.name


class OrganisationNodeAutocompleteView(LoginRequiredMixin, ac.Select2QuerySetView):
    def get_queryset(self):
        queryset = models.OrganisationTreeNode.objects.exclude(level=0)
        if self.q:
            queryset = queryset.filter(
                Q(name__icontains=self.q)|
                Q(parent__name__icontains=self.q) |
                Q(parent__parent__name__icontains=self.q))
        return queryset

    def get_result_label(self, result):
        return result.title

    def get_result_value(self, result):
        return result.id


class OrganisationDocsGenerateCurrentView(generic.View):
    def get(self, request, *args, **kwargs):
        organisation = get_object_or_404(models.OrganisationTreeNode, id=kwargs.get('pk', None))
        manager = OrganisationsDocumentManager(organisation=organisation, date=date.today())
        manager.make_documents()
        return redirect(reverse_lazy('organisation:docs', args=(organisation.id, )))


def send_document(request, pk, type):
    from sendfile import sendfile
    docs_storage = get_object_or_404(models.OrganisationDocumentsContainer, id=int(pk))
    filename = docs_storage.payment
    if type == 'agreement':
        filename = docs_storage.agreement
    return sendfile(request, filename, attachment=True)



