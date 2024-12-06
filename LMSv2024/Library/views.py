from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User, Group
from django.http import HttpResponse
from .forms import UserRegistratioForm
from .models import ISBN, Language, Membership, Author, Category, Book, IssuedBook
from django.contrib import messages
from datetime import date



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
        #we will be getting username and password through Post
        user_req_form= UserRegistratioForm(request.POST)
        if user_req_form.is_valid():
            #create the form, but will not save it
            new_user= user_req_form.save(commit=False)
            

            #set the password after validation
            #checking password == confirm password
            #password value is assigned to password field
            new_user.set_password(user_req_form.cleaned_data['password'])
            new_user.save()
            group = Group.objects.get(name='student')
            new_user.groups.add(group)
             #save to db
            return render(request, 'register_done.html',{'user_req_form':user_req_form})
        
    else:
        user_req_form= UserRegistratioForm()
    return render(request, 'register.html',{'user_req_form':user_req_form})



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


# Authors CRUD (Librarian only)
@login_required
@user_passes_test(is_librarian)
def manage_authors(request):
    authors = Author.objects.all()
    if request.method == "POST":
        name = request.POST.get("name")
        bio = request.POST.get("biography")
        dob = request.POST.get("date_of_birth")
        dod = request.POST.get("date_of_death")
        Author.objects.create(name=name, biography=bio, date_of_birth=dob, date_of_death=dod)
        messages.success(request, "Author added successfully!")
        return redirect("manage_authors")
    return render(request, "book_operations/manage_authors.html", {"authors": authors})

# Update Author
@login_required
@user_passes_test(is_librarian)
def update_author(request, author_id):
    author = get_object_or_404(Author, id=author_id)
    if request.method == "POST":
        author.name = request.POST.get("name")
        author.biography = request.POST.get("biography")
        author.date_of_birth = request.POST.get("date_of_birth")
        author.date_of_death = request.POST.get("date_of_death")
        author.save()
        messages.success(request, "Author updated successfully!")
        return redirect("manage_authors")
    return render(request, "book_operations/update_author.html", {"author": author})

# Delete Author
@login_required
@user_passes_test(is_librarian)
def delete_author(request, author_id):
    author = get_object_or_404(Author, id=author_id)
    if request.method == "POST":
        author.delete()
        messages.success(request, "Author deleted successfully!")
        return redirect("manage_authors")
    return render(request, "book_operations/delete_author.html", {"author": author})



# Categories CRUD (Librarian only)
@login_required
@user_passes_test(is_librarian)
def manage_categories(request):
    categories = Category.objects.all()
    if request.method == "POST":
        name = request.POST.get("name")
        description = request.POST.get("description")
        Category.objects.create(name=name, description=description)
        messages.success(request, "Category added successfully!")
        return redirect("manage_categories")
    return render(request, "book_operations/manage_categories.html", {"categories": categories})

# Update Category
@login_required
@user_passes_test(is_librarian)
def update_category(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    if request.method == "POST":
        category.name = request.POST.get("name")
        category.description = request.POST.get("description")
        category.save()
        messages.success(request, "Category updated successfully!")
        return redirect("manage_categories")
    return render(request, "book_operations/update_category.html", {"category": category})

# Delete Category
@login_required
@user_passes_test(is_librarian)
def delete_category(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    if request.method == "POST":
        category.delete()
        messages.success(request, "Category deleted successfully!")
        return redirect("manage_categories")
    return render(request, "book_operations/delete_category.html", {"category": category})


def is_librarian(user):
    return user.groups.filter(name='Librarian').exists()

# Books CRUD (Librarian only)
@login_required
@user_passes_test(is_librarian)
def manage_books(request):
    books = Book.objects.all()
    authors = Author.objects.all()
    categories = Category.objects.all()
    languages = Language.objects.all()
    isbns = ISBN.objects.all()

    if request.method == "POST":
        title = request.POST.get("title")
        author_id = request.POST.get("author")
        category_id = request.POST.get("category")
        language_id = request.POST.get("language")
        isbn_id = request.POST.get("isbn")
        quantity = request.POST.get("quantity")
        description = request.POST.get("description")
        price = request.POST.get("price")
        book_image = request.FILES.get("book_image")

        author = get_object_or_404(Author, id=author_id)
        category = get_object_or_404(Category, id=category_id)
        language = get_object_or_404(Language, id=language_id)
        isbn = get_object_or_404(ISBN, id=isbn_id)

        # Create the book object
        Book.objects.create(
            title=title,
            author=author,
            category=category,
            language=language,
            isbn=isbn,
            quantity=quantity,
            description=description,
            price=price,
            book_image=book_image,
            added_by=request.user
        )

        messages.success(request, "Book added successfully!")
        return redirect("manage_books")

    return render(request, "book_operations/manage_books.html", {
        "books": books,
        "authors": authors,
        "categories": categories,
        "languages": languages,
        "isbns": isbns
    })


# Update Book
@login_required
@user_passes_test(is_librarian)
def update_book(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    authors = Author.objects.all()
    categories = Category.objects.all()
    if request.method == "POST":
        book.title = request.POST.get("title")
        author_id = request.POST.get("author")
        category_id = request.POST.get("category")
        book.quantity = request.POST.get("quantity")
        book.description = request.POST.get("description")
        book.author = get_object_or_404(Author, id=author_id)
        book.category = get_object_or_404(Category, id=category_id)
        book.save()
        messages.success(request, "Book updated successfully!")
        return redirect("manage_books")
    return render(request, "book_operations/update_book.html", {"book": book, "authors": authors, "categories": categories})

# Delete Book
@login_required
@user_passes_test(is_librarian)
def delete_book(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    if request.method == "POST":
        book.delete()
        messages.success(request, "Book deleted successfully!")
        return redirect("manage_books")
    return render(request, "book_operations/delete_book.html", {"book": book})


# Issue Books (Librarian only)
@login_required
@user_passes_test(is_librarian)
def issue_book(request):
    books = Book.objects.filter(quantity__gt=0)
    users = User.objects.filter(groups__name="Student")
    if request.method == "POST":
        book_id = request.POST.get("book")
        user_id = request.POST.get("user")
        book = get_object_or_404(Book, id=book_id)
        user = get_object_or_404(User, id=user_id)
        IssuedBook.objects.create(book=book, user=user, issue_date=date.today())
        book.quantity -= 1
        book.save()
        messages.success(request, "Book issued successfully!")
        return redirect("issue_book")
    return render(request, "issue_book.html", {"books": books, "users": users})


# View Issued Books (Librarian and Student)
@login_required
def view_issued_books(request):
    if is_librarian(request.user):
        issued_books = IssuedBook.objects.all()
    elif is_student(request.user):
        issued_books = IssuedBook.objects.filter(user=request.user)
    else:
        return HttpResponse("Access Denied", status=403)
    return render(request, "view_issued_books.html", {"issued_books": issued_books})

