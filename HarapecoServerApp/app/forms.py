"""
Definition of forms.
"""

from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.utils.translation import ugettext_lazy as _

class BootstrapAuthenticationForm(AuthenticationForm):
    """Authentication form which uses boostrap CSS."""
    username = forms.CharField(max_length=254,
                               widget=forms.TextInput({
                                   'class': 'form-control',
                                   'placeholder': 'User name'}))
    password = forms.CharField(label=_("Password"),
                               widget=forms.PasswordInput({
                                   'class': 'form-control',
                                   'placeholder':'Password'}))

class GroupCreateForm(forms.Form):
    name = forms.CharField(max_length=60, required=True)
    explain = forms.CharField(max_length=200, required=True)
    auto_belong = forms.CharField(max_length=1, required=True)

class GroupDeleteForm(forms.Form):
    id = forms.IntegerField()

class GroupJoinForm(forms.Form):
    id = forms.IntegerField()

class GroupJoinAllowForm(forms.Form):
    id = forms.IntegerField(required=True)
    allow_status = forms.CharField(max_length=1, required=True)

class MailInformationForm(forms.Form):
    email = forms.EmailField(max_length=70)
    username = forms.CharField(max_length=100)

class RegisterCompleteForm(forms.Form):
    id = forms.CharField(max_length=50)
    password = forms.CharField(max_length=50)

class SetTemporaryPassForm(forms.Form):
    email = forms.CharField(max_length=70)