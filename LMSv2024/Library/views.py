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

def is_student(user):
    return user.groups.filter(name='Student').exists()

### ---------- User Registration and Authentication Views ---------- ###

# User registration view


def register(request):
    if request.method == 'POST':
        user_req_form = UserRegistratioForm(request.POST)
        if user_req_form.is_valid():
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
                # Handle the case where the group does not exist
                pass
            
            # Render success page
            return render(request, 'register_done.html', {'user': new_user})
    else:
        user_req_form = UserRegistratioForm()
    return render(request, 'register.html', {'user_req_form': user_req_form})



# User login view
def login_user(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            if is_librarian(user):
                return redirect("librarian_dashboard")
            elif is_student(user):
                return redirect("student_dashboard")
            else:
                logout(request)
                messages.error(request, "Invalid role. Contact admin.")
                return redirect("login_user")
        else:
            messages.error(request, "Invalid credentials")
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






@login_required
def student_dashboard(request):
    """
    View for the student dashboard after login.
    Displays books, membership plans, and profile details based on user's membership status.
    """
    user = request.user
    membership = user.usermembership_set.first()  # Get the first membership associated with the user

    # Get all books
    books = Book.objects.all()

    # Get all membership plans
    memberships = Membership.objects.all()

    context = {
        'user': user,
        'membership': membership,
        'books': books,
        'memberships': memberships,
    }
    return render(request, 'student_dashboard.html', context)


@login_required
def my_membership(request, membership_id):
    """
    View to handle membership payment and subscription.
    """
    # Get the selected membership plan
    membership = get_object_or_404(Membership, id=membership_id)

    if request.method == 'POST':
        # Record the payment
        Payment.objects.create(
            user=request.user,
            amount=membership.price_per_month,
            payment_date=date.today(),
            payment_type='MEMBERSHIP',
        )

        # Calculate the start date and end date (one month from today)
        start_date = date.today()
        end_date = start_date + timedelta(days=30)

        # Create or update the UserMembership
        user_membership, created = UserMembership.objects.update_or_create(
            user=request.user,
            membership=membership,
            defaults={
                'start_date': start_date,
                'end_date': end_date,
            },
        )

        # Redirect the user to the student dashboard after successful payment
        return redirect('student_dashboard')

    # Render the membership payment page with membership details
    context = {
        'membership': membership,
    }
    return render(request, 'student/my_membership.html', context)



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
    return render(request, 'student/available_books.html', context)


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
    return render(request, 'student/purchase_list.html', context)



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


