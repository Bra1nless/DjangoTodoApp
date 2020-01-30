from django import forms
from .models import TodoItem


class AddTaskForm(forms.Form):
    description = forms.CharField(max_length=128, label='')


class TodoItemForm(forms.ModelForm):
    class Meta:
        model = TodoItem
        fields = ('description', 'priority')
        labels = {'description': 'Описание', 'priority': ''}


class TodoItemExportForm(forms.Form):
    prio_high = forms.BooleanField(label='Высокий приоритет', initial=True, required=False)
    prio_med = forms.BooleanField(label='Средний приоритет', initial=True, required=False)
    prio_low = forms.BooleanField(label='Низкий приоритет', initial=False, required=False)
