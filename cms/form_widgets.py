from django import forms
from django.forms.widgets import Input


class FloatInput(Input):

    def __init__(self):
        self.input_type = 'float'
        self.attrs = {'step': '0.1'}
        self.template_name = 'django/forms/widgets/number.html'
        super(FloatInput, self).__init__()


class TagWidget(forms.widgets.TextInput):
    template_name = 'widgets/tag.html'

    class Media:
        js = ('js/jquery.amsify.suggestags.js', 'js/inittags.js')
        css = {
            'all': ('css/amsify.suggestags.css',)
        }
