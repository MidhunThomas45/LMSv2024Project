from django.db import models
from django.contrib.auth.models import User
from datetime import date
from django.utils import timezone

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
    users = models.ManyToManyField(User, related_name='memberships', through='UserMembership')

    def __str__(self):
        return self.name


# Intermediary table to manage user memberships with additional fields
class UserMembership(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    membership = models.ForeignKey(Membership, on_delete=models.CASCADE)
    start_date = models.DateField(default=date.today)
    end_date = models.DateField(blank=True, null=True)

    def __str__(self):
        return f"{self.user.username} - {self.membership.name}"


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


# Book model to store book details
class Book(models.Model):
    title = models.CharField(max_length=150)
    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    quantity = models.PositiveIntegerField(default=1)
    Book_image = models.ImageField(upload_to="Book_image", null=True, blank=True)
    description = models.TextField(blank=True, null=True)
    Language= models.CharField(max_length=150)
    added_by = models.ForeignKey(User, on_delete=models.CASCADE)
    add_time = models.TimeField(default=timezone.now)
    add_date = models.DateField(default=date.today)

    class Meta:
        unique_together = ("title", "author")

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
