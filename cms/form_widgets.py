from django.forms.widgets import Input


class FloatInput(Input):

    def __init__(self):
        self.input_type = 'float'
        self.attrs = {'step': '0.1'}
        self.template_name = 'django/forms/widgets/number.html'
        super(FloatInput, self).__init__()
