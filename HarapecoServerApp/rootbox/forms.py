from django import forms

class RootBoxDrawForm(forms.Form):
    term_id = forms.IntegerField()
    times = forms.IntegerField()
