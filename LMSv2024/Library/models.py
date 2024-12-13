from django.db import models
from django.contrib.auth.models import User
from datetime import date, timedelta
from django.utils import timezone

# Author model to store author details
class Author(models.Model):
    name = models.CharField(max_length=200)
    biography = models.TextField(blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    date_of_death = models.DateField(blank=True, null=True)

    def __str__(self):
        return self.name


# Category model to store book categories
class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name


# Language model to store available languages
class Language(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class ISBN(models.Model):
    isbn_number = models.CharField(max_length=13, unique=True)
    book_content = models.TextField(blank=True, null=True)  # New Field to store book content

    def __str__(self):
        return self.isbn_number


# Book model to store book details
class Book(models.Model):
    title = models.CharField(max_length=150)
    author = models.ForeignKey('Author', on_delete=models.CASCADE)
    category = models.ForeignKey('Category', on_delete=models.SET_NULL, null=True, blank=True)
    language = models.ForeignKey('Language', on_delete=models.SET_NULL, null=True, blank=True)
    isbn = models.ForeignKey('ISBN', on_delete=models.CASCADE, null=True, blank=True)  # New Field
    quantity = models.PositiveIntegerField(default=1)
    book_image = models.ImageField(upload_to="Book_image", null=True, blank=True)
    description = models.TextField(blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)  # New Field
    added_by = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    add_time = models.TimeField(default=timezone.now)
    add_date = models.DateField(default=date.today)

    class Meta:
        unique_together = ("title", "author")

    def save(self, *args, **kwargs):
        if not self.isbn:
            # Automatically generate and assign an ISBN if not already provided
            isbn_instance = ISBN.objects.create()
            self.isbn = isbn_instance
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


# IssuedBook model to store issued book details
class IssuedBook(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    issue_date = models.DateField(default=date.today)
    return_date = models.DateField(blank=True, null=True)

    @property
    def is_returned(self):
        return self.return_date is not None

    def __str__(self):
        return f"{self.book.title} issued by {self.user.username} on {self.issue_date}"


# Payment model to store payment details
class Payment(models.Model):
    PAYMENT_TYPES = [
        ('Membership', 'Membership'),
        ('Purchase', 'Purchase'),
        ('Rent', 'Rent'),
    ]
    
    PAYMENT_METHOD = [
        ('Card', 'Card'),
        ('UPI', 'UPI'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateTimeField(auto_now_add=True)
    payment_type = models.CharField(max_length=20, choices=PAYMENT_TYPES)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD, default='Card')  # Set a default value

    def __str__(self):
        return f"{self.user.username} - {self.payment_type} - {self.amount} - {self.payment_method}"


# Membership model to store membership details
class Membership(models.Model):
    MEMBERSHIP_CHOICES = [
        ('GOLD', 'Gold'),
        ('PLATINUM', 'Platinum'),
        ('DIAMOND', 'Diamond'),
    ]
    name = models.CharField(max_length=20, choices=MEMBERSHIP_CHOICES, unique=True)
    price_per_month = models.DecimalField(max_digits=6, decimal_places=2)
    book_access_percentage = models.PositiveIntegerField(help_text="Percentage of books accessible with this plan")
    

    def __str__(self):
        return self.name



class UserMembership(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    membership = models.ForeignKey(Membership, on_delete=models.CASCADE)
    start_date = models.DateField(default=date.today)
    end_date = models.DateField(blank=True, null=True)
    payment = models.ForeignKey('Payment', on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} - {self.membership.name} membership"



# Rent model to store rental details
class Rent(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    start_date = models.DateField(auto_now_add=True)
    rental_fee = models.DecimalField(max_digits=6, decimal_places=2)
    payment = models.ForeignKey(Payment, on_delete=models.SET_NULL, null=True, blank=True)  # Added foreign key to Payment

    @property
    def end_date(self):
        return self.start_date + timedelta(days=30)

    def __str__(self):
        return f"{self.user.username} rented {self.book.title}"


# Purchase model to store book purchase details
class Purchase(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    purchase_date = models.DateTimeField(auto_now_add=True)
    delivery_address = models.TextField()
    purchase_price = models.DecimalField(max_digits=6, decimal_places=2)
    payment = models.ForeignKey(Payment, on_delete=models.SET_NULL, null=True, blank=True)  # Added foreign key to Payment

    def __str__(self):
        return f"{self.user.username} purchased {self.book.title}"


    

class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    message = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    

    def _str_(self):
        return f"Notification for {self.user.username}:{self.message}"
    

class comments(models.Model):
    book_comments=models.ForeignKey(Book,on_delete=models.CASCADE)
    comment_text=models.TextField()
    comment_published_datetime=models.DateTimeField(auto_now_add=True)

    def _str_(self):
        return self.comment_text
    
class Reviews(models.Model):
    stars=(
        (1,'one star'),
        (2,'two star'),
        (3,'three star'),
        (4,'four star'),
        (5,'five star')
    )
    post=models.ForeignKey(Book,related_name='review_of_book', on_delete=models.CASCADE)
    rating=models.PositiveSmallIntegerField(choices=stars,default=1)
    title=models.CharField(max_length=200)
    description =models.TextField(blank=True)
    review_author=models.ForeignKey(User,default=1 ,on_delete=models.CASCADE)

    def _str_(self):
        return self.title