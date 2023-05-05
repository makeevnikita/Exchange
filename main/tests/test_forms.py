from django.test import TestCase, tag
from django import forms
from django.forms import widgets
from main.forms import FeedBackForm
from main.models import FeedBack



class FormsTest(TestCase):

    @tag('fast')
    def test_feedback_form(self):
        
        form = FeedBackForm()
    
        self.assertIsInstance(
            obj=form.fields['text'],
            cls=forms.CharField
        )
        self.assertIsInstance(
            obj=form.fields['text'].widget,
            cls=widgets.Textarea
        )
        self.assertEqual(
            first=form.fields['text'].widget.attrs['placeholder'],
            second='Оставьте отзыв'
        )
        self.assertEqual(
            first=form.fields['text'].widget.attrs['class'],
            second='form-feedback'
        )
        self.assertEqual(
            first=form.fields['text'].widget.attrs['maxlength'],
            second=FeedBack._meta.get_field('text').max_length
        )
        self.assertEqual(
            first=form.fields['text'].label,
            second='Отзыв'
        )
        self.assertTupleEqual(
            tuple1=('text',),
            tuple2=form.Meta.fields
        )
        self.assertIs(
            expr1=form.Meta.model,
            expr2=FeedBack
        )
