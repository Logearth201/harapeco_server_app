from django import forms

class RootBoxDrawForm(forms.Form):
    term_id = forms.IntegerField()
    times = forms.IntegerField()

class RootBoxSeedSetForm(forms.Form):
    term_id = forms.IntegerField()
    hash_key = forms.CharField(max_length=100)