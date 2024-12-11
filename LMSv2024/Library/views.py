from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User, Group
from django.http import HttpResponse
from django.contrib import messages
from django.db.models import Q
from datetime import date, timedelta, timezone

from .forms import UserRegistratioForm, BookForm, AuthorForm, CategoryForm, PaymentForm
from .models import ISBN, Language, Membership, Author, Category, Book, IssuedBook, Rent, Purchase, Payment, UserMembership




def landing_page(request):
    return render(request, "landing_page.html")

# Utility function to check roles
def is_librarian(user):
    return user.groups.filter(name='Librarian').exists()



### ---------- User Registration and Authentication Views ---------- ###

# User registration view

from django.core.exceptions import ValidationError

# User registration view
def register(request):
    if request.method == 'POST':
        user_req_form = UserRegistratioForm(request.POST)
        if user_req_form.is_valid():
            # Check if username already exists
            if User.objects.filter(username=user_req_form.cleaned_data['username']).exists():
                messages.error(request, "Username already taken. Please choose a different one.")
                return render(request, 'register.html', {'user_req_form': user_req_form})

            # Check if email already exists
            if User.objects.filter(email=user_req_form.cleaned_data['email']).exists():
                messages.error(request, "Email already registered. Use a different email.")
                return render(request, 'register.html', {'user_req_form': user_req_form})

            # Create user instance without saving
            new_user = user_req_form.save(commit=False)
            
            # Set the password
            new_user.set_password(user_req_form.cleaned_data['password'])
            new_user.save()

            # Add user to 'student' group
            try:
                group = Group.objects.get(name='student')
                new_user.groups.add(group)
            except Group.DoesNotExist:
                messages.error(request, "Student group does not exist. Contact admin.")
                return redirect('register')
            
            # Render success page
            messages.success(request, "Registration successful. You can now log in.")
            return redirect("login_user")
        else:
            # Highlight errors in the form
            messages.error(request, "Please correct the highlighted errors.")
    else:
        user_req_form = UserRegistratioForm()

    return render(request, 'register.html', {'user_req_form': user_req_form})


# User login view
def login_user(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        # Basic input validations
        if not username or not password:
            messages.error(request, "Both username and password are required.")
            return redirect("login_user")

        user = authenticate(request, username=username, password=password)

        if user is not None:
            # Check if user is active
            if not user.is_active:
                messages.error(request, "Account is inactive. Contact admin for assistance.")
                return redirect("login_user")

            login(request, user)

            # Redirect based on role
            if is_librarian(user):
                return redirect("librarian_dashboard")
            elif is_student(user):
                return redirect("student_dashboard")
            else:
                logout(request)
                messages.error(request, "Invalid role. Contact admin.")
                return redirect("login_user")
        else:
            messages.error(request, "Invalid username or password.")
            return redirect("login_user")

    return render(request, "login.html")



# User logout view
def logout_user(request):
    logout(request)
    return redirect("landing_page")


### ---------- Dashboard Views ---------- ###

@login_required
@user_passes_test(is_librarian)
def librarian_dashboard(request):
    books = Book.objects.all()
    return render(request, "librarian_dashboard.html", {"books": books})



### ---------- CRUD Views for Models ---------- ###

# Membership CRUD (Librarian only)
@login_required
@user_passes_test(is_librarian)
def manage_memberships(request):
    memberships = Membership.objects.all()
    if request.method == "POST":
        name = request.POST.get("name")
        price = request.POST.get("price")
        percentage = request.POST.get("percentage")
        Membership.objects.create(name=name, price_per_month=price, book_access_percentage=percentage)
        messages.success(request, "Membership added successfully!")
        return redirect("manage_memberships")
    return render(request, "manage_memberships.html", {"memberships": memberships})




# Books Management
def manage_books(request):
    query = request.GET.get('q', '')
    print(f"Search Query: {query}")  # Debugging line

    books = Book.objects.all()

    # Apply search filter if a query is provided
    if query:
        books = books.filter(Q(title__icontains=query) | Q(author__name__icontains=query))

    # Initialize an empty form for rendering purposes
    form = BookForm()

    if request.method == 'POST':
        if 'add' in request.POST:
            form = BookForm(request.POST, request.FILES)  # Bind form data for adding a book
            if form.is_valid():
                form.save()
                messages.success(request, 'Book added successfully!')
                return redirect('manage_books')
            else:
                messages.error(request, 'Error adding the book. Please check the form.')
        elif 'update' in request.POST:
            book_id = request.POST.get('book_id')
            if not book_id:
                messages.error(request, 'Book ID is required to update a book.')
                return redirect('manage_books')

            book = get_object_or_404(Book, id=book_id)
            form = BookForm(request.POST, request.FILES, instance=book)  # Bind form data for updating the book
            if form.is_valid():
                form.save()
                messages.success(request, 'Book updated successfully!')
                return redirect('manage_books')
            else:
                messages.error(request, 'Error updating the book. Please check the form.')

    return render(request, 'book_operations/manage_books.html', {'books': books, 'query': query, 'form': form})



def delete_book(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    book.delete()
    messages.success(request, 'Book deleted successfully!')
    return redirect('manage_books')



# Manage Authors - List and Search
def manage_authors(request):
    query = request.GET.get('q', '')
    authors = Author.objects.all()
    if query:
        authors = authors.filter(name__icontains=query)
    return render(request, 'book_operations/manage_authors.html', {'authors': authors, 'query': query})

# Add Author
def add_author(request):
    if request.method == 'POST':
        form = AuthorForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Author added successfully!')
            return redirect('manage_authors')
    else:
        form = AuthorForm()
    return render(request, 'book_operations/add_author.html', {'form': form})

# Edit Author
def edit_author(request, author_id):
    author = get_object_or_404(Author, id=author_id)
    if request.method == 'POST':
        form = AuthorForm(request.POST, instance=author)
        if form.is_valid():
            form.save()
            messages.success(request, 'Author updated successfully!')
            return redirect('manage_authors')
    else:
        form = AuthorForm(instance=author)
    return render(request, 'book_operations/edit_author.html', {'form': form, 'author': author})

# Delete Author
def delete_author(request, author_id):
    author = get_object_or_404(Author, id=author_id)
    author.delete()
    messages.success(request, 'Author deleted successfully!')
    return redirect('manage_authors')



# List and Search Categories
def manage_categories(request):
    query = request.GET.get('q', '')  # Search query
    categories = Category.objects.all()
    if query:
        categories = categories.filter(name__icontains=query)

    return render(request, 'book_operations/manage_categories.html', {'categories': categories, 'query': query})


# Add Category
def add_category(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Category added successfully!')
            return redirect('manage_categories')
    else:
        form = CategoryForm()
    return render(request, 'book_operations/add_category.html', {'form': form})


# Update Category
def update_category(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, 'Category updated successfully!')
            return redirect('manage_categories')
    else:
        form = CategoryForm(instance=category)
    return render(request, 'book_operations/update_category.html', {'form': form, 'category': category})


# Delete Category
def delete_category(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    category.delete()
    messages.success(request, 'Category deleted successfully!')
    return redirect('manage_categories')



# Check if user is a librarian
def is_librarian(user):
    return user.groups.filter(name='Librarian').exists()

# Manage Books - List and Search
@login_required
@user_passes_test(is_librarian)
def manage_books(request):
    query = request.GET.get('q', '')  # Search query
    books = Book.objects.all().order_by('category__name', 'title')  # List books category-wise

    if query:
        books = books.filter(title__icontains=query)

    return render(request, 'book_operations/manage_books.html', {'books': books, 'query': query})

# Add Book
@login_required
@user_passes_test(is_librarian)
def add_book(request):
    if request.method == "POST":
        form = BookForm(request.POST, request.FILES)
        if form.is_valid():
            book = form.save(commit=False)
            book.added_by = request.user  # Automatically add the librarian
            book.save()
            messages.success(request, "Book added successfully!")
            return redirect('manage_books')
    else:
        form = BookForm()
    return render(request, 'book_operations/add_book.html', {'form': form})

# Update Book
@login_required
@user_passes_test(is_librarian)
def update_book(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    if request.method == "POST":
        form = BookForm(request.POST, request.FILES, instance=book)
        if form.is_valid():
            form.save()
            messages.success(request, "Book updated successfully!")
            return redirect('manage_books')
    else:
        form = BookForm(instance=book)
    return render(request, 'book_operations/update_book.html', {'form': form, 'book': book})

# Delete Book
@login_required
@user_passes_test(is_librarian)
def delete_book(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    if request.method == "POST":
        book.delete()
        messages.success(request, "Book deleted successfully!")
        return redirect('manage_books')
    return render(request, 'book_operations/delete_book.html', {'book': book})





# Helper function to check if the user is a student
def is_student(user):
    return user.groups.filter(name='Student').exists()

@login_required
@user_passes_test(is_student)
def student_dashboard(request):
    """
    Student dashboard showing books, membership plans, purchased membership details, and payment history.
    """
    user = request.user
    user_membership = UserMembership.objects.filter(user=user).first()  # Fetch user's active membership
    memberships = Membership.objects.all()  # All available membership plans
    books = Book.objects.all()  # All books in the system

    # Fetch the payment history for the user
    payments = Payment.objects.filter(user=user)  # Assuming you have a Payment model

    # Restrict book access based on membership plan
    if user_membership:
        access_percentage = user_membership.membership.book_access_percentage  # Fetch access limit percentage
        total_books = books.count()
        access_limit = int(total_books * (access_percentage / 100))  # Calculate the number of books user can access
        books = books[:access_limit]  # Restrict books to the calculated limit

    context = {
        'user_membership': user_membership,
        'memberships': memberships,
        'books': books,
        'payments': payments,  # Add payment history to the context
    }
    return render(request, 'student_dashboard.html', context)


@login_required
@user_passes_test(is_student)
def take_membership(request, membership_id):
    # Get the membership plan using its ID
    membership = get_object_or_404(Membership, id=membership_id)

    # Retrieve the price of the membership plan
    amount = membership.price_per_month

    # Create a payment record
    payment = Payment.objects.create(
        user=request.user,
        amount=amount,
        payment_type="Membership",
        payment_method="Card"  # Default payment method; can be dynamic based on user input
    )

    # Calculate membership duration (e.g., 30 days for one month)
    start_date = date.today()
    end_date = start_date + timedelta(days=30)

    # Create or update the user's membership
    user_membership, created = UserMembership.objects.update_or_create(
        user=request.user,
        defaults={
            "membership": membership,
            "start_date": start_date,
            "end_date": end_date,
            "payment": payment,
        },
    )

    # Show success message
    if created:
        messages.success(request, f"You have successfully subscribed to the {membership.name} plan.")
    else:
        messages.info(request, f"Your {membership.name} membership has been updated.")

    # Redirect to a success page or membership dashboard
    return redirect("membership_dashboard")  # Replace with the actual URL name for your membership dashboard


# Librarian-only view to manage memberships
@login_required
@user_passes_test(lambda user: user.groups.filter(name='Librarian').exists())
def manage_memberships(request):
    memberships = Membership.objects.all()

    if request.method == "POST":
        name = request.POST.get("name")
        price = request.POST.get("price")
        percentage = request.POST.get("percentage")
        Membership.objects.create(name=name, price_per_month=price, book_access_percentage=percentage)
        messages.success(request, "Membership added successfully!")
        return redirect("manage_memberships")

    return render(request, "manage_memberships.html", {"memberships": memberships})



@login_required
def available_books(request):
    """
    View to display available books based on user's membership plan.
    """
    user = request.user
    membership = user.usermembership_set.first()

    if membership:
        percentage = membership.membership.book_access_percentage
        accessible_books_count = Book.objects.count() * percentage // 100
        accessible_books = Book.objects.all()[:accessible_books_count]
        rent_books = Book.objects.all()[accessible_books_count:]
    else:
        accessible_books = []
        rent_books = Book.objects.all()

    context = {
        'accessible_books': accessible_books,
        'rent_books': rent_books,
    }
    return render(request, 'student/rent_book.html', context)


@login_required
def rent_book(request, book_id):
    """
    View to rent a book for non-accessible books based on membership.
    """
    book = get_object_or_404(Book, id=book_id)
    rent_fee = book.price * 0.1  # 10% of the book price

    Rent.objects.create(
        user=request.user,
        book=book,
        rent_start_date=date.today(),
        rent_fee=rent_fee,
    )
    return redirect('available_books')


@login_required
def purchase_book(request, book_id):
    """
    View to purchase a book.
    """
    book = get_object_or_404(Book, id=book_id)

    if request.method == 'POST':
        Purchase.objects.create(
            user=request.user,
            book=book,
            purchase_date=date.today(),
            delivery_address=request.POST.get('delivery_address'),
        )
        return redirect('student_dashboard')

    context = {
        'book': book,
    }
    return render(request, 'student/purchase_book.html', context)


@login_required
def rent_list(request):
    """
    View to display the list of rented books by the user.
    """
    rents = Rent.objects.filter(user=request.user)
    context = {'rents': rents}
    return render(request, 'student/rent_list.html', context)


@login_required
def purchase_list(request):
    """
    View to display the list of purchased books by the user.
    """
    purchases = Purchase.objects.filter(user=request.user)
    context = {'purchases': purchases}
    return render(request, 'student/purchased_books.html', context)



def create_payment(user: User, amount: float, payment_type: str):
    """
    Creates a payment record for the user.

    Args:
        user (User): The user who is making the payment.
        amount (float): The amount of the payment.
        payment_type (str): The type of payment ('Membership', 'Purchase', 'Rent').

    Returns:
        Payment: The created Payment object.
    """
    if payment_type not in ['Membership', 'Purchase', 'Rent']:
        raise ValueError("Invalid payment type. Valid types are 'Membership', 'Purchase', 'Rent'.")

    # Create the payment object
    payment = Payment.objects.create(
        user=user,
        amount=amount,
        payment_date=timezone.now(),  # Automatically set the payment date
        payment_type=payment_type
    )

    # Return the created Payment object
    return payment


#users list
def user_list(request):
    query = request.GET.get('q')
    students_group = Group.objects.get(name='Student')
    students = User.objects.filter(groups=students_group)

    if query:
        students = students.filter(username__icontains=query) | students.filter(email__icontains=query) | students.filter(first_name__icontains=query)

    return render(request, 'user_list.html', {'users': students, 'query': query})




@login_required
def make_payment(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    
    if request.method == 'POST':
        payment_method = request.POST.get('payment_method')
        if payment_method not in ['Card', 'UPI']:
            messages.error(request, "Invalid payment method.")
            return redirect('make_payment', book_id=book_id)
        
        # Create Payment object
        payment = Payment.objects.create(
            user=request.user,
            amount=book.price,
            payment_type='Purchase',
            payment_method=payment_method,
            book=book,
            delivery_address=request.POST.get('delivery_address') if request.POST.get('delivery_address') else None,
        )

        # Redirect to invoice page
        messages.success(request, "Payment successful!")
        return redirect('invoice', payment_id=payment.id)

    return render(request, 'payment/make_payment.html', {'book': book})

# views.py
@login_required
def invoice(request, payment_id):
    payment = get_object_or_404(Payment, id=payment_id)
    
    context = {
        'payment': payment,
        'user': payment.user,
        'book': payment.book,
    }
    return render(request, 'payment/invoice.html', context)

@login_required
def payment_history(request):
    # Get all payments made by the current user
    payments = Payment.objects.filter(user=request.user)

    context = {
        'payments': payments
    }
    return render(request, 'payment/payment_history.html', context)



@login_required
def take_membership(request, membership_id):
    membership = get_object_or_404(Membership, id=membership_id)
    amount = membership.price_per_month  # Calculate membership price based on plan
    try:

        user_membership=UserMembership.objects.get(user=request.user)
    except UserMembership.DoesNotExist:
        user_membership=None
    memberships = Membership.objects.all()


    if request.method == 'POST':
        payment_method = request.POST.get('payment_method')
        if payment_method not in ['Card', 'UPI']:
            messages.error(request, "Invalid payment method.")
            return redirect('take_membership', membership_id=membership.id)
        
        # Create Payment object for Membership
        payment = Payment.objects.create(
            user=request.user,
            amount=amount,
            payment_type='Membership',
            payment_method=payment_method,
        )

        # Redirect to invoice page
        messages.success(request, "Membership payment successful!")
        return redirect('invoice', payment_id=payment.id)
    context= {'membership': membership,'user_membership':user_membership,'memberships':memberships,}

    return render(request, 'take_membership.html',context)


#for taking membership
# def take_membership(request, membership_id):
#     """
#     View to display the selected membership plan and allow the user to proceed with the payment.
#     """
#     # Get the selected membership plan using the provided membership_id
#     membership = get_object_or_404(Membership, id=membership_id)
#     memberships = Membership.objects.all()
#     user_membership=UserMembership.objects.get(user=request.user)
#     print(f'u{user_membership}')
#     context = {
#         'membership': membership,
#         'memberships': memberships,  # Pass the full membership details to the template
#         'user_membership':user_membership
#     }

#     return render(request, 'take_membership.html', context)


from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Payment, Membership

@login_required
def membership_payment(request, membership_id):
    membership = Membership.objects.get(id=membership_id)

    if request.method == 'POST':
        payment_method = request.POST.get('payment_method')
        amount = membership.price_per_month

        if payment_method:
            # Save the payment details to the database
            payment=Payment.objects.create(
                user=request.user,
                amount=amount,
                payment_type='Membership',
                payment_method=payment_method,
            )
            messages.success(request, "Payment successful!")
            # Calculate the start date and end date (one month from today)
            start_date = date.today()
            end_date = start_date + timedelta(days=30)

            # Create or update the UserMembership
            UserMembership.objects.update_or_create(
                user=request.user,
                membership=membership,
                payment=payment,
                defaults={
                    'start_date': start_date,
                    'end_date': end_date,
                },
            )

            return redirect('payment_success')  # Replace with your success page URL name

        else:
            messages.error(request, "Please select a payment method.")

    return render(request, 'payment.html', {'membership': membership})



@login_required
def my_membership(request, membership_id):
    """
    View to handle membership payment and subscription.
    """
    # Get the selected membership plan
    membership = get_object_or_404(Membership, id=membership_id)
    user_membership=UserMembership.objects.get(user=request.user)
    print(f'u{user_membership}')
    if request.method == 'POST':
        payment_method = request.POST.get('payment_method')

        # Simulate processing the payment method
        if payment_method == 'credit_card':
            card_number = request.POST.get('card_number')
            expiry_date = request.POST.get('expiry_date')
            cvv = request.POST.get('cvv')
            # Process the credit card payment (e.g., with a payment gateway)

        elif payment_method == 'paypal':
            paypal_email = request.POST.get('paypal_email')
            # Process the PayPal payment (e.g., with PayPal API)

        elif payment_method == 'bank_transfer':
            bank_account = request.POST.get('bank_account')
            bank_name = request.POST.get('bank_name')
            # Process the bank transfer payment (e.g., through bank integration)

        # Record the payment after processing
        Payment.objects.create(
            user=request.user,
            amount=membership.price_per_month,
            payment_date=date.today(),
            payment_type='MEMBERSHIP',
        )

        
        # Redirect the user to the payment success page after successful payment
        return redirect('payment_success')  # Make sure this matches the URL name

    # Render the membership payment page with membership details
    return render(request, 'take_membership.html', {'membership': membership,'user_membership':user_membership})

@login_required
def payment_success(request):
    return render(request, 'payment_success.html')

from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa  # Install with `pip install xhtml2pdf`

def download_invoice(request, payment_id):
    # Fetch payment details
    payment = Payment.objects.get(id=payment_id)
    membership = payment.user.usermembership.membership  # Assuming UserMembership relationship

    # Context for invoice
    context = {
        'payment': payment,
        'membership': membership,
    }

    # Load template
    template = get_template('payment/invoice_template.html')  # Create this template
    html = template.render(context)

    # Generate PDF
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="Invoice_{payment.id}.pdf"'
    pisa_status = pisa.CreatePDF(html, dest=response)

    if pisa_status.err:
        return HttpResponse('Error generating PDF', status=500)

    return response
