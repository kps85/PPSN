from django.shortcuts import get_object_or_404, render
from django.http import HttpResponse
from Programmierpraktikum.settings import MEDIA_ROOT, MEDIA_URL

from .models import User, Group, Message

# Create your views here.

def index(request):
	user_list = User.objects.all()
	message_list = Message.objects.select_related('user')
	#user_list = User.objects.all()
	#message_list = Message.objects.all()
	#message_list = Message.objects.all().select_related('user')
	group_list = Group.objects.all()
	context = { 'user_list': user_list , 'message_list': message_list }
	
	return render(request, 'twittur/index_test.html', context)

