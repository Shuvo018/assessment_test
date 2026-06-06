from django import forms
from django.forms import inlineformset_factory
from .models import Test, Question, Option


class TestForm(forms.ModelForm):
    class Meta:
        model  = Test
        fields = ["title", "description", "duration_minutes", "status", "start_time", "end_time"]
        widgets = {
            "title":            forms.TextInput(attrs={"placeholder": "Test title"}),
            "description":      forms.Textarea(attrs={"rows": 3, "placeholder": "Optional description"}),
            "duration_minutes": forms.NumberInput(attrs={"min": 1}),
            "status":           forms.Select(),
            "start_time":       forms.DateTimeInput(attrs={"type": "datetime-local"}, format="%Y-%m-%dT%H:%M"),
            "end_time":         forms.DateTimeInput(attrs={"type": "datetime-local"}, format="%Y-%m-%dT%H:%M"),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["start_time"].input_formats = ["%Y-%m-%dT%H:%M"]
        self.fields["end_time"].input_formats   = ["%Y-%m-%dT%H:%M"]
        for field in self.fields.values():
            field.required = field.label in ["Title", "Duration minutes"]


class QuestionForm(forms.ModelForm):
    class Meta:
        model  = Question
        fields = ["question_text", "points", "order_index"]
        widgets = {
            "question_text": forms.Textarea(attrs={"rows": 2, "placeholder": "Enter question"}),
            "points":        forms.NumberInput(attrs={"min": 1}),
            "order_index":   forms.HiddenInput(),
        }


class OptionForm(forms.ModelForm):
    class Meta:
        model  = Option
        fields = ["option_label", "option_text", "is_correct"]
        widgets = {
            "option_label": forms.Select(),
            "option_text":  forms.TextInput(attrs={"placeholder": "Option text"}),
            "is_correct":   forms.CheckboxInput(),
        }


OptionFormSet = inlineformset_factory(
    Question, Option,
    form=OptionForm,
    extra=4,
    max_num=4,
    can_delete=False,
)