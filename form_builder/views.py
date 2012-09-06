from django.utils import simplejson
from django.utils.translation import ugettext_lazy as _
from django import shortcuts
from django.core import urlresolvers
from django.views import generic
from django import http

from autocomplete_light import modelform_factory
from crispy_forms.helper import FormHelper

from models import Form, KIND_CHOICES


class FormCreateView(generic.CreateView):
    model = Form
    template_name = 'form_builder/form_create.html'

    def get_success_url(self):
        return urlresolvers.reverse('form_builder_form_update',
            args=(self.object.pk,))


class FormUpdateView(generic.UpdateView):
    model = Form
    template_name = 'form_builder/form_update.html'

    def get_context_data(self, *args, **kwargs):
        context = super(FormUpdateView, self).get_context_data(*args,
            **kwargs)

        model = self.object.contenttype.model_class()

        context['KIND_CHOICES'] = KIND_CHOICES

        return context

    def post(self, *args, **kwargs):
        form_dict = simplejson.loads(self.request.POST['form'])
        form_model = self.get_object()
        form_model.update_from_dict(form_dict)
        form_model.save()

        return http.HttpResponse(_(u'Form updated with success'))


class ObjectCreateView(generic.TemplateView):
    template_name = 'form_builder/object_form.html'
    form_kwargs = {}

    @property
    def form_model(self):
        return shortcuts.get_object_or_404(Form, pk=self.kwargs['form_pk'])

    @property
    def form_class(self):
        form = modelform_factory(self.form_model.contenttype.model_class())
        form.helper = FormHelper()
        form.helper.layout = self.form_model.to_crispy()
        return form

    @property
    def form_instance(self):
        form_instance = getattr(self, '_form_instance', None)
        if form_instance is None:
            self._form_instance = self.form_class(*self.form_args,
                **self.form_kwargs)
        return self._form_instance

    @property
    def form_args(self):
        if self.request.method == 'POST':
            return (self.request.POST, self.request.FILES)
        return []

    def get_context_data(self, *args, **kwargs):
        context = super(ObjectCreateView, self).get_context_data(*args,
                **kwargs)

        context['form'] = self.form_instance
        context['form_model'] = self.form_model

        return context

    def post(self, request, *args, **kwargs):
        if self.form_instance.is_valid():
            obj = self.form_instance.save()
            return http.HttpResponseRedirect(urlresolvers.reverse(
                'form_builder_object_update', args=(obj.pk,
                    self.kwargs.get('form_pk'))))

        return super(ObjectCreateView, self).get(request, *args, **kwargs)


class ObjectUpdateView(ObjectCreateView):
    @property
    def form_kwargs(self):
        return {'instance': shortcuts.get_object_or_404(
            self.form_model.contenttype.model_class(), pk=self.kwargs['pk'])}
