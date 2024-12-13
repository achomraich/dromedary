from django.shortcuts import render

from tutorials.helpers import login_prohibited

"""
This file contains a view function to handle 
Home
"""

@login_prohibited
def home(request):
    """Display the application's start/home screen."""

    return render(request, 'home.html')