from django.views.generic.edit import DeleteView, UpdateView
from django.views.generic import DetailView, FormView
from django.shortcuts import get_object_or_404, reverse, render, redirect
from django.http import Http404

from back_office.mixins import ContextMixin, LoginRequiredMixin
from shortener.utils import encode
from shortener.models import URL
from . import forms
from . import models


class DocCreateView(ContextMixin, FormView):
    form_class = forms.DocForm
    template_name = 'docs/doc_form.html'

    def post(self, request, *args, **kwargs):
        form = forms.DocForm(request.POST or None, request.FILES or None)
        if form.is_valid():
            suggestion = form.cleaned_data.get('suggestion')
            instance = form.save(commit=False)
            shortened = encode(suggestion)
            link = 'http://' + request.get_host() + reverse(
                "docs:doc_detail", kwargs={
                    "url": shortened
                })
            user = request.user if request.user.is_authenticated else None
            url = models.URL.objects.create(
                link=link, shortened=shortened, user=user)
            instance.url = url
            instance.save()
            return redirect(instance.get_absolute_url())
        else:
            return self.form_invalid(form)

    def get(self, request):
        context = {"form": forms.DocForm(), 'page_title': 'Create Awesome Doc'}
        return render(request, "docs/doc_form.html", context)


class DocDeleteView(DeleteView):
    model = models.Doc
    success_url = '/'

    def get(self, request, *args, **kwargs):
        raise Http404

    def get_object(self):
        url_arg = self.kwargs['url']
        url = get_object_or_404(URL, shortened=url_arg)
        instance = get_object_or_404(models.Doc, url=url)
        if url.user != self.request.user:
            raise Http404
        url.delete()
        return instance


class DocDetailView(ContextMixin, DetailView):
    model = models.Doc
    context_object_name = 'doc'
    context = {'page_title': 'Doc'}

    def get_object(self, queryset=None):
        url_arg = self.kwargs['url']
        url = get_object_or_404(URL, shortened=url_arg)
        instance = get_object_or_404(models.Doc, url=url)
        return instance


class DocUpdateView(LoginRequiredMixin, UpdateView):
    model = models.Doc
    fields = ['title', 'content']

    def get_object(self, queryset=None):
        url_arg = self.kwargs['url']
        url = get_object_or_404(URL, shortened=url_arg)
        instance = get_object_or_404(models.Doc, url=url)
        if url.user != self.request.user:
            raise Http404
        return instance
