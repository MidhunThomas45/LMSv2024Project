from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User, Group
from django.http import HttpResponse
from django.contrib import messages
from django.db.models import Q
from datetime import date
from .forms import UserRegistratioForm, BookForm, AuthorForm, CategoryForm
from .models import ISBN, Language, Membership, Author, Category, Book, IssuedBook

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


@login_required
@user_passes_test(is_student)
def student_dashboard(request):
    issued_books = IssuedBook.objects.filter(user=request.user)
    return render(request, "student_dashboard.html", {"issued_books": issued_books})


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






