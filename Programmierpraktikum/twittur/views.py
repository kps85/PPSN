from django.shortcuts import get_object_or_404, render
from django.http import HttpResponse

from .models import User, Group

# Create your views here.

def index(request):
	user_list = User.objects.all()
	group_list = Group.objects.all()
	context = { 'user_list': user_list , 'group_list': group_list }
	
	return render(request, 'index.html', context)
    
    
def login(request):
	return render(request, 'ftu.html')

def info(request):
	return render(request, 'info.html')

def settings(request):
	return render(request, 'settings.html')
