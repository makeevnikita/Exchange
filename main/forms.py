from django import forms
from django.forms import widgets
from .models import FeedBack



class FeedBackForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):

        super(FeedBackForm, self).__init__(*args, **kwargs)

        self.fields['text'] = forms.CharField(
            widget=widgets.Textarea(
                attrs={
                    'placeholder': 'Оставьте отзыв',
                    'class': 'form-feedback',
                    'maxlength': FeedBack._meta.get_field('text').max_length,
                },
            ),
            label='Отзыв',
        )

    class Meta:
        model = FeedBack
        fields = ('text',)