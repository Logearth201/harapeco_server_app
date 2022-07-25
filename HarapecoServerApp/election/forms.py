from django import forms

class ElectionForm(forms.Form):
    submit_id = forms.IntegerField()
    candidate_id = forms.IntegerField()
