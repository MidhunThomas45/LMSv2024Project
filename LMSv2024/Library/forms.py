from django import forms
from .models import User
from django.forms import ValidationError


class UserRegistratioForm(forms.ModelForm): #using ModelForm
    #password
    password= forms.CharField(
        label='Password',
        widget=forms.PasswordInput
    )
    #for confirm password
    password2= forms.CharField(
        label='Confirm Password',
        widget=forms.PasswordInput
    )

    #since inheritance from ModelForm, I can use the model to declare the fields
    class Meta:
        model= User
        #fields in the built in Model User
        fields= ('username','first_name','email','password')

        #overriding a inbuilt method to check the password input = confirm password
        #clean_<fieldname>
        def clean_password2(self):
            cd= self.cleaned_data
            if cd['password'] != cd['password2']:
                raise ValidationError('Password does not match!!!')
            
            return cd['password2']