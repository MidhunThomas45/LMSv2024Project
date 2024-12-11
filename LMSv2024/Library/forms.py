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
        widget=forms.PasswordInput,
        min_length=8,  # Add minimum length for password
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

    # Validate password strength
    def clean_password(self):
        password = self.cleaned_data.get('password')
        
        # Check for at least one digit
        if not re.search(r'\d', password):
            raise ValidationError('Password must contain at least one digit.')

        # Check for at least one lowercase letter
        if not re.search(r'[a-z]', password):
            raise ValidationError('Password must contain at least one lowercase letter.')

        # Check for at least one uppercase letter
        if not re.search(r'[A-Z]', password):
            raise ValidationError('Password must contain at least one uppercase letter.')

        # Check for at least one special character
        if not re.search(r'[@$!%*?&]', password):
            raise ValidationError('Password must contain at least one special character.')

        return password

    # Ensure the username is unique
    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise ValidationError('Username is already taken.')
        return username

    # Ensure the email is unique
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError('This email address is already associated with another account.')
        return email

        




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