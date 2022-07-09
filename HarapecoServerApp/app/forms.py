"""
Definition of forms.
"""

from urllib import request
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

class UserLoginForm(forms.Form):
    email = forms.CharField(max_length=70)
    password = forms.CharField(max_length=30)
    push_notification_token = forms.CharField(max_length=500, required=False)

class AutoLoginForm(forms.Form):
    user_id = forms.CharField(max_length=30, required=False)
    auth_key = forms.CharField(max_length=200, required=False)
    push_notification_token = forms.CharField(max_length=500, required=False)

class UserLogoutForm(forms.Form):
    auth_key = forms.CharField(max_length=200, required=False)

class UserInfoChangeForm(forms.Form):
    email = forms.EmailField(max_length=70, required=False)
    username = forms.CharField(max_length=100, required=False)

class UserInfoChangeCompleteForm(forms.Form):
    password = forms.CharField(max_length=50)

class InviteTokenForm(forms.Form):
    token = forms.CharField(max_length=100)