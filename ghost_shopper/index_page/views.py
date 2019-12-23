from django.shortcuts import render, redirect
from django.views import generic

from . import models
from . import forms


class IndexView(generic.TemplateView):
    template_name = 'index_page/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['callback_form'] = forms.CallbackForm()
        context['working_steps'] = models.WorkingStep.objects.all()
        return context

    def post(self, request, *args, **kwargs):
        form = forms.CallbackForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('index_page:index')
        else:
            context = self.get_context_data()
            context['callback_form'] = form
            return render(request, self.template_name, context)


class IndexPageUpdateView(generic.View):
    template_name = 'index_page/update.html'

    def get(self, request, *args, **kwargs):
        context = {
            'form': forms.IndexPageForm(instance=models.IndexPage.load())
        }
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        form = forms.IndexPageForm(instance=models.IndexPage.load(), data=request.POST, files=request.FILES)
        if form.is_valid():
            form.save()
            form = forms.IndexPageForm(instance=models.IndexPage.load())
        return render(request, self.template_name, {'form': form})


class CallbackFormListView(generic.ListView):
    model = models.CallbackForm





