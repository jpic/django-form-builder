from django.utils import simplejson
from django.utils.translation import ugettext_lazy as _
from django import shortcuts
from django.core import urlresolvers
from django.views import generic
from django import http
from django.forms.models import inlineformset_factory
from django.db.models.fields.related import ForeignRelatedObjectsDescriptor

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
    def model_class(self):
        model_class = getattr(self, '_model_class', None)
        if model_class is None:
            self._model_class = self.form_model.contenttype.model_class()
        return self._model_class

    @property
    def form_model(self):
        form_model = getattr(self, '_form_model', None)
        if form_model is None:
            self._form_model = shortcuts.get_object_or_404(Form,
                pk=self.kwargs['form_pk'])
        return self._form_model

    @property
    def form_class(self):
        attributes = self.form_model.enabled_field_set

        form = modelform_factory(self.form_model.contenttype.model_class(),
            fields=[a.model_field_name for a in attributes])

        for attribute in attributes:
            name = attribute.model_field_name

            if attribute.name:
                form.base_fields[name].label = attribute.name

            if attribute.help_text:
                form.base_fields[name].help_text = attribute.help_text

        form.helper = FormHelper()
        form.helper.layout = self.form_model.to_crispy()
        form.helper.form_tag = False
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

    @property
    def inline_instances(self):
        inline_instances = []

        for name, value in self.model_class.__dict__.items():
            if not isinstance(value, ForeignRelatedObjectsDescriptor):
                continue

            model = getattr(self.model_class, name).related.model

            cls = inlineformset_factory(self.model_class, model,
                form=modelform_factory(model), extra=25)

            instance = cls(prefix=name, *self.inline_args,
                **self.inline_kwargs)
            instance.name = instance.model._meta.verbose_name_plural
            inline_instances.append(instance)

        return inline_instances

    @property
    def inline_kwargs(self):
        return {'instance': self.form_instance.instance}

    @property
    def inline_args(self):
        return self.form_args

    def get_context_data(self, *args, **kwargs):
        context = super(ObjectCreateView, self).get_context_data(*args,
                **kwargs)

        context['form'] = self.form_instance
        context['form_model'] = self.form_model
        context['inlines'] = self.inline_instances

        return context

    def post(self, request, *args, **kwargs):
        valid = self.form_instance.is_valid()
        for inline in self.inline_instances:
            if not inline.is_valid():
                valid = False

        if valid:
            obj = self.form_instance.save()
            [inline.save() for inline in self.inline_instances]
            return http.HttpResponseRedirect(urlresolvers.reverse(
                'form_builder_object_update', args=(obj.pk,
                    self.kwargs.get('form_pk'))))

        return super(ObjectCreateView, self).get(request, *args, **kwargs)


class ObjectUpdateView(ObjectCreateView):
    @property
    def form_kwargs(self):
        return {'instance': shortcuts.get_object_or_404(
            self.form_model.contenttype.model_class(), pk=self.kwargs['pk'])}
