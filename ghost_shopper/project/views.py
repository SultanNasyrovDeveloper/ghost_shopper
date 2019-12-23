from dal import autocomplete as ac
from django_filters.views import FilterView
from django.shortcuts import render, redirect, get_object_or_404
from django.views import generic
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.decorators import method_decorator

from ghost_shopper.auth.decorators import staff_member_required

from ghost_shopper.check.enums import CHECK_TYPES

from .models import Project
from .filters import ProjectSearch
from .forms import ProjectForm, ProjectCheckTemplateForm


@method_decorator(staff_member_required, name='dispatch')
class ProjectListView(LoginRequiredMixin, FilterView):
    model = Project
    context_object_name = 'projects'
    template_name = 'project/list.html'
    filterset_class = ProjectSearch
    paginate_by = 20
    login_url = reverse_lazy('auth:login')


@method_decorator(staff_member_required, name='dispatch')
class ProjectCreateView(LoginRequiredMixin, generic.View):

    login_url = reverse_lazy('auth:login')

    def get(self, request, *args, **kwargs):
        context = {
            'project_form': ProjectForm(prefix='project'),
            'check_template_form': ProjectCheckTemplateForm(prefix='check')
        }
        return render(request, 'project/create.html', context)

    def post(self, request, *args, **kwargs):
        project_form = ProjectForm(request.POST, prefix='project')
        check_template_form = ProjectCheckTemplateForm(request.POST, prefix='check')
        if project_form.is_valid():
            project = project_form.save()
            if check_template_form.is_valid():
                check_template = check_template_form.save()
                check_template.type = CHECK_TYPES['TEMPLATE']
                check_template.project = project
                check_template.save()
                return redirect(project.get_absolute_url())
            else:
                return render(request, 'project/create.html', {
                    'project_form': project_form, 'check_template_form': check_template_form})
        else:
            return render(request, 'project/create.html', {
                'project_form': project_form, 'check_template_form': check_template_form})


@method_decorator(staff_member_required, name='dispatch')
class ProjectDetailView(LoginRequiredMixin, generic.DetailView):

    model = Project
    template_name = 'project/detail.html'
    context_object_name = 'project'
    login_url = reverse_lazy('auth:login')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['check_template'] = self.get_object().get_check_template()
        return context


@method_decorator(staff_member_required, name='dispatch')
class ProjectUpdateView(LoginRequiredMixin, generic.UpdateView):

    login_url = reverse_lazy('auth:login')

    def get(self, request, *args, **kwargs):
        project = get_object_or_404(Project, id=kwargs.get('pk', None))
        check_template = project.get_check_template()
        context = {
            'project_form': ProjectForm(prefix='project', instance=project),
            'check_template_form': ProjectCheckTemplateForm(prefix='check', instance=check_template)
        }
        return render(request, 'project/create.html', context)

    def post(self, request, *args, **kwargs):
        project = get_object_or_404(Project, id=kwargs.get('pk', None))
        check_template = project.get_check_template()
        project_form = ProjectForm(request.POST, prefix='project', instance=project)
        check_template_form = ProjectCheckTemplateForm(request.POST, prefix='check', instance=check_template)
        if project_form.is_valid():
            project = project_form.save()
            if check_template_form.is_valid():
                check_template = check_template_form.save()
                check_template.save()
                return redirect(project.get_absolute_url())
            else:
                return render(request, 'project/create.html', {
                    'project_form': project_form, 'check_template_form': check_template_form})
        else:
            return render(request, 'project/create.html', {
                'project_form': project_form, 'check_template_form': check_template_form})


@method_decorator(staff_member_required, name='dispatch')
class ProjectDeleteView(LoginRequiredMixin, generic.DeleteView):
    model = Project
    template_name = 'base/confirm_delete.html'
    success_url = reverse_lazy('project:list')
    login_url = reverse_lazy('auth:login')


@method_decorator(staff_member_required, name='dispatch')
class ProjectChecksMultiplyView(LoginRequiredMixin, generic.View):

    login_url = reverse_lazy('auth:login')

    def get(self, request, *args, **kwargs):
        context = {
            'project': get_object_or_404(Project, id=kwargs.get('pk', None))
        }
        return render(request, 'project/multiply_confirm.html', context)

    def post(self, request, *args, **kwargs):
        project = get_object_or_404(Project, id=kwargs.get('pk', None))
        project.multiply_checks()
        return redirect(project.get_absolute_url())


class ProjectNameAutocomplete(LoginRequiredMixin, ac.Select2QuerySetView):
    def get_queryset(self):
        queryset = Project.objects.all()
        if self.q:
            queryset.filter(name__icontains=self.q)
        return queryset

    def get_result_label(self, result):
        return result.name

    def get_result_value(self, result):
        return result.name