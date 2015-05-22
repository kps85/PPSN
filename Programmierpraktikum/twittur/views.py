from django.shortcuts import get_object_or_404, render
from django.http import HttpResponse

from .models import User, Group

# Create your views here.

def index(request):
	user_list = User.objects.all()
	group_list = Group.objects.all()
	context = { 'user_list': user_list , 'group_list': group_list }
	
	return render(request, 'twittur/index.html', context)

