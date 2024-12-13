from django.contrib.auth.models import Group

def user_roles(request):
    if request.user.is_authenticated:
        is_librarian = request.user.groups.filter(name='Librarian').exists()
        return {'is_librarian': is_librarian}
    return {'is_librarian':False}