from django import forms
from django.contrib.auth.forms import AuthenticationForm

class LoginForm(AuthenticationForm):
	username = forms.CharField(widget=forms.TextInput(attrs={'class':'input_bottom_outline full_width username', 'placeholder':"Username or Phone or Email"}))
	password = forms.CharField(widget=forms.PasswordInput(attrs={'class':'input_bottom_outline full_width', 'placeholder':"Password"}))