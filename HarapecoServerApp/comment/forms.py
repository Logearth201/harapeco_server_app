from django import forms

class CommentCreationForm(forms.Form):
    text = forms.CharField(max_length=4000, required=True)
    id = forms.IntegerField()


