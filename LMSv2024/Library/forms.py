from django import forms
from .models import User, Book, Author, Category, ISBN, Payment, Purchase
from django.core.exceptions import ValidationError
import re
from django import forms
from .models import Membership


from django import forms
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
import re

class UserRegistratioForm(forms.ModelForm):
    # Password
    password = forms.CharField(
        label='Password',
        widget=forms.PasswordInput
    )
    # Confirm password
    password2 = forms.CharField(
        label='Confirm Password',
        widget=forms.PasswordInput
    )

    class Meta:
        model = User
        fields = ('username', 'first_name', 'email')

    # Ensure passwords match
    def clean_password2(self):
        cd = self.cleaned_data
        if cd.get('password') != cd.get('password2'):
            raise ValidationError('Passwords do not match!')
        return cd['password2']

        




class BookForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = [
            'title', 'author', 'category', 'language', 'isbn', 
            'quantity', 'book_image', 'description', 'price'
        ]


class AuthorForm(forms.ModelForm):
    class Meta:
        model = Author
        fields = ['name', 'biography', 'date_of_birth', 'date_of_death']

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'description']





class PaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = ['payment_type']  # Membership or Purchase Payment


class PurchaseForm(forms.ModelForm):
    class Meta:
        model = Purchase
        fields = ['delivery_address']  # Capture delivery address for book purchase



class MembershipForm(forms.ModelForm):
    class Meta:
        model = Membership
        fields = ['name', 'price_per_month', 'book_access_percentage']
        widgets = {
            'name': forms.Select(choices=Membership.MEMBERSHIP_CHOICES),
            'price_per_month': forms.NumberInput(attrs={'class': 'form-control'}),
            'book_access_percentage': forms.NumberInput(attrs={'class': 'form-control'}),
        }

from django import forms
from .models import Rent

class RentForm(forms.ModelForm):
    class Meta:
        model = Rent
        fields = ['user', 'book', 'rental_fee']  # Exclude 'start_date', it will be auto-filled