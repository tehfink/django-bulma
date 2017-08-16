from django import forms, VERSION as django_version
from django.template import Context
from django.template.loader import get_template
from django import template

register = template.Library()

BULMA_COLUMN_COUNT = 1

@register.filter
def bulma(element):
    markup_classes = {'label': '', 'value': '', 'single_value': ''}
    return render(element, markup_classes)


@register.filter
def bulma_inline(element):
    markup_classes = {'label': 'sr-only', 'value': '', 'single_value': ''}
    return render(element, markup_classes)


@register.filter
def bulma_horizontal(element, label_cols='is-2'):

    markup_classes = {'label': label_cols, 'value': '', 'single_value': ''}

    for cl in label_cols.split(' '):
        splitted_class = cl.split('-')

        try:
            value_nb_cols = int(splitted_class[-1])
        except ValueError:
            value_nb_cols = BULMA_COLUMN_COUNT

        if value_nb_cols >= BULMA_COLUMN_COUNT:
            splitted_class[-1] = BULMA_COLUMN_COUNT
        else:
            offset_class = cl.split('-')
            offset_class[-1] = 'offset-' + str(value_nb_cols)
            splitted_class[-1] = str(BULMA_COLUMN_COUNT - value_nb_cols)
            markup_classes['single_value'] += ' ' + '-'.join(offset_class)
            markup_classes['single_value'] += ' ' + '-'.join(splitted_class)

        markup_classes['value'] += ' ' + '-'.join(splitted_class)

    return render(element, markup_classes)

@register.filter
def add_input_classes(field):
    if not is_checkbox(field) and not is_multiple_checkbox(field) \
       and not is_radio(field) and not is_file(field):
        field_classes = field.field.widget.attrs.get('class', '')
        field_classes += ' control'
        field.field.widget.attrs['class'] = field_classes


def render(element, markup_classes):
    element_type = element.__class__.__name__.lower()

    if element_type == 'boundfield':
        add_input_classes(element)
        template = get_template("bulma/forms/field.html")
        context = Context({'field': element, 'classes': markup_classes, 'form': element.form})
    else:
        has_management = getattr(element, 'management_form', None)
        if has_management:
            for form in element.forms:
                for field in form.visible_fields():
                    add_input_classes(field)

            template = get_template("bulma/forms/formset.html")
            context = Context({'formset': element, 'classes': markup_classes})
        else:
            for field in element.visible_fields():
                add_input_classes(field)

            template = get_template("bulma/forms/form.html")
            context = Context({'form': element, 'classes': markup_classes})

        if django_version >= (1, 8):
            context = context.flatten()

    return template.render(context)


@register.filter
def widget_type(field):
        return field.field.widget


@register.filter
def is_select(field):
    return isinstance(field.field.widget, forms.Select)


@register.filter
def is_textarea(field):
    return isinstance(field.field.widget, forms.Textarea)


@register.filter
def is_input(field):
    return isinstance(field.field.widget, (forms.TextInput, forms.EmailInput, forms.PasswordInput))


@register.filter
def is_checkbox(field):
    return isinstance(field.field.widget, forms.CheckboxInput)


@register.filter
def is_multiple_checkbox(field):
    return isinstance(field.field.widget, forms.CheckboxSelectMultiple)


@register.filter
def is_radio(field):
    return isinstance(field.field.widget, forms.RadioSelect)


@register.filter
def is_file(field):
    return isinstance(field.field.widget, forms.FileInput)


@register.filter
def addclass(field, css_class):
    return field.as_widget(attrs={"class":css_class})
