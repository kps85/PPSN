from django.shortcuts import get_object_or_404, render
from django.http import HttpResponse
from Programmierpraktikum.settings import MEDIA_ROOT, MEDIA_URL

<<<<<<< HEAD
from .models import User, Group, Nav


=======
from .models import User, Group, Message
>>>>>>> master



# Create your views here.
def index(request):
	user_list = User.objects.all()
	message_list = Message.objects.select_related('user')
	#user_list = User.objects.all()
	#message_list = Message.objects.all()
	#message_list = Message.objects.all().select_related('user')
	group_list = Group.objects.all()
<<<<<<< HEAD
	context = { 'active_page' : 'index', 'user_list': user_list , 'group_list': group_list, 'nav': Nav.nav }
	return render(request, 'index.html', context)
    

def login(request):
    context = { 'active_page' : 'ftu', 'nav': Nav.nav}
    return render(request, 'ftu.html', context)
	
def profile(request):
	user_list = User.objects.all()
	group_list = Group.objects.all()
	context = { 'active_page' : 'profile', 'user_list': user_list , 'group_list': group_list, 'nav': Nav.nav}
	return render(request, 'profile.html', context)

def info(request):
    context = { 'active_page' : 'info', 'nav': Nav.nav}
    return render(request, 'info.html', context)
=======
	context = { 'user_list': user_list , 'message_list': message_list }
	
	return render(request, 'twittur/index_test.html', context)
>>>>>>> master

def settings(request):
    context = { 'active_page' : 'settings', 'nav': Nav.nav}
    return render(request, 'settings.html', context)
