from django.db import models
from django.utils.translation import ugettext_lazy as _

from not_eav.models import Attribute, KIND_CHOICES
from crispy_forms.layout import Layout, Fieldset, ButtonHolder, Submit


class Form(models.Model):
    name = models.CharField(max_length=100)
    contenttype = models.ForeignKey('contenttypes.ContentType')

    def __unicode__(self):
        return u'%s / %s' % (self.contenttype.model, self.name)

    def to_crispy(self, enabled=True):
        layout = Layout()
        for tab in self.tab_set.filter(enabled=enabled):
            layout.fields.append(tab.to_crispy())

        return layout

    @property
    def enabled_tab_set(self):
        return self.tab_set.filter(enabled=True)

    @property
    def disabled_tab_set(self):
        return self.tab_set.filter(enabled=False)

    @property
    def enabled_field_set(self):
        return Field.objects.filter(tab__in=self.enabled_tab_set)

    def update_from_dict(self, data):
        order = 0
        for tab_data in data:
            if tab_data.get(u'id', None):
                tab = Tab.objects.get(pk=tab_data[u'id'])
                tab.name = tab_data[u'name']
            else:
                tab = Tab(name=tab_data[u'name'], form=self)
            tab.enabled = True
            tab.order = order
            tab.save()
            order += 1

            tab.update_from_dict(tab_data)


def prepare_form(sender, instance, created, **kwargs):
    if not created:
        return

    model_class = instance.contenttype.model_class()
    default_tab, c = instance.tab_set.get_or_create(name=u'Disabled',
            enabled=False)

    for field in model_class._meta.fields + model_class._meta.many_to_many:
        try:
            f = Field.objects.get(model_field_name=field.name,
                tab__form=instance)
        except Field.DoesNotExist:
            f = Field(model_field_name=field.name, tab=default_tab,
                    name=getattr(field, 'verbose_name', _(field.name)))
            f.save()

    if not instance.tab_set.filter(enabled=True).count():
        instance.tab_set.create(name='Info', enabled=True)

models.signals.post_save.connect(prepare_form, sender=Form)


def clean_form(sender, instance, **kwargs):
    instance.tab_set.annotate(fields=models.Count('field')).filter(
        fields=0).delete()
models.signals.post_save.connect(clean_form, sender=Form)


class Tab(models.Model):
    name = models.CharField(max_length=100)
    form = models.ForeignKey('Form')
    order = models.IntegerField(default=0)
    enabled = models.BooleanField(default=False)

    class Meta:
        ordering = ('order',)

    def __unicode__(self):
        return u'%s / %s' % (self.name, self.form)

    def to_crispy(self):
        fieldset = Fieldset(self.name)
        for field in self.field_set.all():
            fieldset.fields.append(field.to_crispy())
        return fieldset

    def update_from_dict(self, data):
        order = 0
        for field_data in data[u'fields']:
            if field_data.get(u'id', None):
                field = Field.objects.get(pk=field_data[u'id'])
            else:
                field = Field(tab=self,
                    model_field_name=field_data[u'model_field_name'])
            field.tab = self
            field.name = field_data[u'name']
            field.kind = field_data[u'kind']
            field.help_text = field_data[u'help_text']
            field.order = order
            field.save()
            order += 1


class Field(models.Model):
    name = models.CharField(max_length=100)
    model_field_name = models.CharField(max_length=100)
    help_text = models.TextField(blank=True)
    tab = models.ForeignKey('Tab')
    kind = models.CharField(max_length=12, choices=KIND_CHOICES)
    order = models.IntegerField(default=0)

    class Meta:
        ordering = ('order',)

    def __unicode__(self):
        return u'%s / %s' % (self.name, self.tab)

    def to_crispy(self):
        return self.model_field_name


def create_field_attribute(sender, instance, **kwargs):
    try:
        instance.tab.form.contenttype.model_class()._meta.get_field_by_name(
            instance.model_field_name)
        return
    except models.FieldDoesNotExist:
        pass

    kwargs = dict(content_type=instance.tab.form.contenttype,
        name=instance.model_field_name)

    try:
        attribute = Attribute.objects.get(**kwargs)
    except Attribute.DoesNotExist:
        attribute = Attribute(**kwargs)

    attribute.kind = instance.kind
    attribute.verbose_name = instance.name
    attribute.help_text = instance.help_text
    attribute.save()
models.signals.post_save.connect(create_field_attribute, sender=Field)
