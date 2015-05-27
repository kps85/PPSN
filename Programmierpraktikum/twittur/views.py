from django.shortcuts import get_object_or_404, render
from django.http import HttpResponse, HttpResponseRedirect
from Programmierpraktikum.settings import MEDIA_ROOT, MEDIA_URL
from django.contrib.auth.models import User

from django.contrib.auth import authenticate, login
from django.contrib import auth
from .models import UserProfile, Group, Nav, Message






# Create your views here.

def index(request):
	if not request.user.is_authenticated():
		return HttpResponseRedirect('/twittur/login/')
	user_list = User.objects.all()
	message_list = Message.objects.select_related('user')
	#user_list = User.objects.all()
	#message_list = Message.objects.all()
	#message_list = Message.objects.all().select_related('user')
	group_list = Group.objects.all()

	context = { 'active_page' : 'index', 'user_list': user_list , 'group_list': group_list, 'nav': Nav.nav }
	return render(request, 'index.html', context)
    

def login(request):


	if request.method == "GET":
		query_dict = request.GET
		username = query_dict.get('username')
		print(username)
		password = query_dict.get('password')
		print(password)
		user = authenticate(username=username, password=password)
		context = { 'active_page' : 'index', 'nav': Nav.nav }
		if user is not None:
			if user.is_active:
				auth.login(request, user)
				return render(request, 'index.html', context)
		else:
			HttpResponseRedirect('/twittur/login/')


	if request.method == 'POST':
		query_dict = request.POST
		username = query_dict.get('name')
		print(username)
		email = query_dict.get('email')
		password = query_dict.get('password')
		print(password)
		user = User.objects.create_user( username, email, password )
		user_profil = UserProfile(user=user, studentNumber=000000, academicDiscipline='Informatik')
		user = authenticate(username = username, password = password)
		context = { 'active_page' : 'index', 'nav': Nav.nav }
		auth.login(request, user)
		return render(request, 'index.html', context)

	context = { 'active_page' : 'ftu', 'nav': Nav.nav}
	return render(request, 'ftu.html', context)


def profile(request):
	if not request.user.is_authenticated():
		return HttpResponseRedirect('/twittur/login/')
	user_list = User.objects.all()
	group_list = Group.objects.all()
	context = { 'active_page' : 'profile', 'user_list': user_list , 'group_list': group_list, 'nav': Nav.nav}
	return render(request, 'profile.html', context)


def info(request):
	if not request.user.is_authenticated():
		return HttpResponseRedirect('/twittur/login/')

	context = { 'active_page' : 'info', 'nav': Nav.nav}
	return render(request, 'info.html', context)


def settings(request):
	if not request.user.is_authenticated():
		return HttpResponseRedirect('/twittur/login/')

	context = { 'active_page' : 'settings', 'nav': Nav.nav}
	return render(request, 'settings.html', context)
