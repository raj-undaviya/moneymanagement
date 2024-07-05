from django.forms import forms, ModelForm
from .models import *

class UserForm(ModelForm):
    class Meta:
        model = Userdata
        fields = ['user_firstname', 'user_lastname', 'user_email']

# class ProfileForm(ModelForm):
#     class Meta:
#         model = Profile
#         fields = ['profile_image']
