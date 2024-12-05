from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User, Group
from django.http import HttpResponse
from .forms import UserRegistratioForm
from .models import Membership, UserMembership, Author, Category, Book, IssuedBook
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
    return render(request, "manage_authors.html", {"authors": authors})


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
    return render(request, "manage_categories.html", {"categories": categories})


# Books CRUD (Librarian only)
@login_required
@user_passes_test(is_librarian)
def manage_books(request):
    books = Book.objects.all()
    authors = Author.objects.all()
    categories = Category.objects.all()
    if request.method == "POST":
        title = request.POST.get("title")
        author_id = request.POST.get("author")
        category_id = request.POST.get("category")
        quantity = request.POST.get("quantity")
        description = request.POST.get("description")
        author = get_object_or_404(Author, id=author_id)
        category = get_object_or_404(Category, id=category_id)
        Book.objects.create(title=title, author=author, category=category, quantity=quantity, description=description, added_by=request.user)
        messages.success(request, "Book added successfully!")
        return redirect("manage_books")
    return render(request, "manage_books.html", {"books": books, "authors": authors, "categories": categories})


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

