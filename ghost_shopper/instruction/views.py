from dal import autocomplete as ac
from django_filters.views import FilterView
from django.views import generic
from django.urls import reverse_lazy
from django.shortcuts import redirect, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.utils.decorators import method_decorator

from ghost_shopper.auth.decorators import staff_member_required

from .models import Instruction
from .forms import InstructionForm
from .filters import InstructionSearch


@method_decorator(staff_member_required, name='dispatch')
class InstructionListView(LoginRequiredMixin, FilterView):

    model = Instruction
    template_name = 'instruction/list.html'
    filterset_class = InstructionSearch
    context_object_name = 'instructions'
    paginate_by = 20
    login_url = reverse_lazy('auth:login')


@method_decorator(staff_member_required, name='dispatch')
class InstructionCreateView(LoginRequiredMixin, generic.CreateView):

    model = Instruction
    template_name = 'instruction/create.html'
    form_class = InstructionForm
    login_url = reverse_lazy('auth:login')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_name'] = 'Создать инструкцию'
        return context

    def form_valid(self, form):
        instruction = form.save()
        return redirect(reverse_lazy('instruction:detail', args=(instruction.id, )))


class InstructionDetailView(LoginRequiredMixin, UserPassesTestMixin, generic.DetailView):

    model = Instruction
    template_name = 'instruction/detail.html'
    context_object_name = 'instruction'
    login_url = reverse_lazy('auth:login')

    def test_func(self):
        # TODO реализовать

        user = self.request.user
        check = get_object_or_404(Instruction, id=self.kwargs.get('pk', None))

        if user.is_performer:
            return True
        elif user.is_customer:
            if user.profile.is_boss:
                return True
            else:
                return False
        elif user.is_staff:
            return True
        else:
            return False


@method_decorator(staff_member_required, name='dispatch')
class InstructionUpdateView(LoginRequiredMixin, generic.UpdateView):

    model = Instruction
    template_name = 'instruction/create.html'
    form_class = InstructionForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_name'] = 'Редактировать инструкцию'
        return context


@method_decorator(staff_member_required, name='dispatch')
class InstructionDeleteView(LoginRequiredMixin, generic.DeleteView):

    model = Instruction
    template_name = 'base/confirm_delete.html'
    success_url = reverse_lazy('instruction:list')
    login_url = reverse_lazy('auth:login')


class InstructionAutocompleteView(LoginRequiredMixin, ac.Select2QuerySetView):

    login_url = reverse_lazy('auth:login')

    def get_queryset(self):
        queryset = Instruction.objects.all()
        if self.q:
            queryset = queryset.filter(name__icontains=self.q)
        return queryset

    def get_result_label(self, result):
        return result.name

    def get_result_value(self, result):
        return result.id


class InstructionSearchAutocompleteView(LoginRequiredMixin, ac.Select2QuerySetView):

    login_url = reverse_lazy('auth:login')

    def get_queryset(self):
        queryset = Instruction.objects.all()
        if self.q:
            queryset = queryset.filter(name__icontains=self.q)
        return queryset

    def get_result_label(self, result):
        return result.name

    def get_result_value(self, result):
        return result.id

