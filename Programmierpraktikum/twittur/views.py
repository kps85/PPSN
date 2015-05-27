from django.shortcuts import get_object_or_404, render
from django.http import HttpResponse, HttpResponseRedirect
from Programmierpraktikum.settings import MEDIA_ROOT, MEDIA_URL
from django.contrib.auth.models import User

from django.contrib.auth import authenticate, login
from django.contrib import auth
from .models import UserProfile, Group, Nav, Message




# startpage
def index(request):

	# redirect, if user is not authenticated 
	if not request.user.is_authenticated():
		return HttpResponseRedirect('/twittur/login/')

	user_list = UserProfile.objects.all()
	message_list = Message.objects.all().select_related('user__userprofile')

	if message_list:
		print('yes')
	else:
		print('no')

	#user_list = User.objects.all()
	#message_list = Message.objects.all()
	#message_list = Message.objects.all().select_related('user')
	group_list = Group.objects.all()

	context = { 'active_page' : 'index', 'user_list': user_list , 'message_list' : message_list ,'group_list': group_list, 'nav': Nav.nav }
	return render(request, 'index.html', context)
    

# login/registration page
def login(request):

	# login
	if request.method == "GET":
		query_dict = request.GET
		username = query_dict.get('username')
		password = query_dict.get('password')
		user = authenticate(username=username, password=password)
		context = { 'active_page' : 'index', 'nav': Nav.nav }

		if user is not None:
			if user.is_active:
				auth.login(request, user)
				return render(request, 'index.html', context)
		else:
			return render(request, 'ftu.html')			

	# Registration
	if request.method == 'POST':
		query_dict = request.POST
		username = query_dict.get('name')
		# check if available
		checkUsername = User.objects.get( username__exact = username )
		print(checkUsername.username)
		print(username)
		if checkUsername.username == username:
			return render(request, 'ftu.html')

		password = query_dict.get('password')
		email = query_dict.get('email')
		user = User.objects.create_user( username, email, password )
		user_profil = UserProfile(user=user, studentNumber=000000, academicDiscipline='Informatik')
		user_profil.save()
		user = authenticate(username = username, password = password)
		context = { 'active_page' : 'index', 'nav': Nav.nav , 'user' : user_profil }
		auth.login(request, user)
		return render(request, 'index.html', context)

	# twitter/login/
	context = { 'active_page' : 'ftu', 'nav': Nav.nav}
	return render(request, 'ftu.html', context)

# profilpage
def profile(request):
	if not request.user.is_authenticated():
		return HttpResponseRedirect('/twittur/login/')
	user_list = User.objects.all()
	group_list = Group.objects.all()
	context = { 'active_page' : 'profile', 'user_list': user_list , 'group_list': group_list, 'nav': Nav.nav}
	return render(request, 'profile.html', context)

# infopage
def info(request):
	if not request.user.is_authenticated():
		return HttpResponseRedirect('/twittur/login/')

	context = { 'active_page' : 'info', 'nav': Nav.nav}
	return render(request, 'info.html', context)

# settingspage
def settings(request):
	if not request.user.is_authenticated():
		return HttpResponseRedirect('/twittur/login/')

	context = { 'active_page' : 'settings', 'nav': Nav.nav}
	return render(request, 'settings.html', context)
