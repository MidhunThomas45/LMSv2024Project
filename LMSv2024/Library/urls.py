from django.urls import path
from .import views

urlpatterns = [
    # Authentication URLs
    path("", views.landing_page, name="landing_page"),
    path("register/", views.register, name="register"),
    path("login/", views.login_user, name="login_user"),
    path("logout/", views.logout_user, name="logout_user"),

    # Dashboard URLs
    path("librarian/dashboard/", views.librarian_dashboard, name="librarian_dashboard"),
    path("student/dashboard/", views.student_dashboard, name="student_dashboard"),

    # Book Management URLs
    path('books/', views.manage_books, name='manage_books'),  # List and search books
    path('books/add/', views.add_book, name='add_book'),  # Add book
    path('books/update/<int:book_id>/', views.update_book, name='update_book'),  # Update book
    path('books/delete/<int:book_id>/', views.delete_book, name='delete_book'),  # Delete book

    # Author Management URLs
    path("authors/", views.manage_authors, name="manage_authors"),  # List and search authors
    path("authors/add/", views.add_author, name="add_author"),  # Add author
    path("authors/edit/<int:author_id>/", views.edit_author, name="edit_author"),  # Edit author
    path("authors/delete/<int:author_id>/", views.delete_author, name="delete_author"),  # Delete author


    # Category Management URLs
    path("categories/", views.manage_categories, name="manage_categories"),  # List and search categories
    path("categories/add/", views.add_category, name="add_category"),  # Add category
    path("categories/update/<int:category_id>/", views.update_category, name="update_category"),  # Update category
    path("categories/delete/<int:category_id>/", views.delete_category, name="delete_category"),  # Delete category


    # Membership URLs (if required)
    path("memberships/", views.manage_memberships, name="manage_memberships"),  # Manage memberships

    # Book Issue and Return
    path("books/issue/", views.issue_book, name="issue_book"),
    path("issued-books/", views.view_issued_books, name="view_issued_books"),
]
