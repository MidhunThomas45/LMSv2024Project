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
     path('student-dashboard/', views.student_dashboard, name='student_dashboard'),
    path('membership/take/<int:membership_id>/', views.take_membership, name='take_membership'),
    path("memberships/", views.manage_memberships, name="manage_memberships"),
    path('available-books/', views.available_books, name='available_books'),
    path('read/<int:rent_id>/', views.read_book, name='read_book'),
    path('rent-book/<int:book_id>/', views.rent_book, name='rent_book'),
    path('payment/<int:rent_id>/', views.process_payment_rent, name='process_payment_rent'),
    path('payment-success/', views.payment_success_rent, name='payment_success_rent'),
    path('purchase-book/<int:book_id>/', views.purchase_book, name='purchase_book'),
    path('rent-list/', views.rent_list, name='rent_list'),
    # path('purchase-list/', views.purchase_list, name='purchase_list'),
    #for displaying users list
    path("users/", views.user_list, name="user_list"),

    #payment
    path('make-payment/<int:book_id>/', views.make_payment, name='make_payment'),
    path('invoice/<int:payment_id>/', views.invoice, name='invoice'),
    path('payment-history/', views.payment_history, name='payment_history'),
    path('membership/take/<int:membership_id>/', views.take_membership, name='take_membership'),

    path('membership/payment/<int:membership_id>/', views.membership_payment, name='membership_payment'),
    
    path('membership/payment/<int:membership_id>/', views.take_membership, name='my_membership'),

    path('membership/payment/success/', views.payment_success, name='payment_success'),
    # path('download-invoice/<int:payment_id>/', views.download_invoice, name='download_invoice'),

    path('student/purchase-books/', views.purchase_books, name='purchase_books'),

   
    path('buy-book/<int:book_id>/', views.buy_book, name='buy_book'),
    path('payment-page/<int:book_id>/', views.payment_page, name='payment_page'),
    
    path('student/purchase-confirmation/<int:book_id>/', views.purchase_confirmation, name='purchase_confirmation'),

    path('purchase-list/', views.purchase_list, name='purchased_books'),
    path('read-book/<int:book_id>/', views.read_book_purchase, name='read_book_purchase'),
]
