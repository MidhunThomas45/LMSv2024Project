from django.urls import path
from .import views

urlpatterns = [
    # Authentication URLs
    path("", views.landing_page, name="landing_page"),

    path('register/', views.register, name='register'),
    path('login/', views.login_user, name='login_user'),
    path('logout/', views.logout_user, name='logout_user'),

    # Dashboard URLs
    path('librarian/dashboard/', views.librarian_dashboard, name='librarian_dashboard'),
    path('student/dashboard/', views.student_dashboard, name='student_dashboard'),

    # Membership URLs (CRUD)
    path('memberships/', views.manage_memberships, name='manage_memberships'),

    # Author URLs (CRUD)
    path('authors/', views.manage_authors, name='manage_authors'),
    path('authors/update/<int:author_id>/', views.update_author, name='update_author'),
    path('authors/delete/<int:author_id>/', views.delete_author, name='delete_author'),


    # Category URLs (CRUD)
    path('categories/', views.manage_categories, name='manage_categories'),
    path('categories/update/<int:category_id>/', views.update_category, name='update_category'),
    path('categories/delete/<int:category_id>/', views.delete_category, name='delete_category'),


    # Book URLs (CRUD)
    path('books/', views.manage_books, name='manage_books'),
    path('books/update/<int:book_id>/', views.update_book, name='update_book'),
    path('books/delete/<int:book_id>/', views.delete_book, name='delete_book'),

    # Issue Book
    path('books/issue/', views.issue_book, name='issue_book'),

    # View Issued Books
    path('issued-books/', views.view_issued_books, name='view_issued_books'),
]
