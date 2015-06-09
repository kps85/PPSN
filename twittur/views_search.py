import copy

from django.db.models import Q
from django.shortcuts import render

from .functions import dbm_to_m
from .models import Message, Nav
from .views import msgDialog


# search input
def search(request):
    search_input = None

    if request.method == 'GET':
        query_dict = request.GET
        search_input = query_dict.get('search')

    # filter all messages contain the word  or all users contain the word
    message_list = Message.objects.all().select_related('user__userprofile') \
        .filter(
        Q(text__contains=search_input) | Q(user__username__contains=search_input)
    ).order_by('-date').distinct('text')
    context = {
        'search': search_input,
        'message_list': message_list,
        'active_page': 'settings',
        'nav': Nav.nav,
        'msgForm': msgDialog(request),
    }
    return render(request, 'search.html', context)


# click on hashtaglinks will redirect to this function.
def hashtag(request, text):
    search_input = text

    # filter all messages contain #
    dbmessage_list = Message.objects.all().filter(hashtags__name=search_input)
    message_list = []
    for message in dbmessage_list:
        copy_message = copy.copy(message)
        message_list.append(dbm_to_m(copy_message))
    message_list = zip(message_list, dbmessage_list)

    context = {
        'search': "#" + search_input,
        'message_list': message_list,
        'active_page': 'settings',
        'nav': Nav.nav,
        'msgForm': msgDialog(request),
    }
    return render(request, 'search.html', context)