from django.shortcuts import render

from tutorials.helpers import login_prohibited

@login_prohibited
def home(request):
    """Display the application's start/home screen."""

    return render(request, 'home.html')