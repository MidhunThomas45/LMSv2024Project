from django import forms
from .models import User, Book, Author, Category, ISBN, Payment, Purchase
from django.core.exceptions import ValidationError
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
