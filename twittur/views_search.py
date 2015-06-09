import copy

from django.db.models import Q
from django.shortcuts import render

from .functions import dbm_to_m
from .models import Message, Nav, UserProfile, Hashtag
from .views import msgDialog
from django.contrib.auth.models import User


# search input
def search(request):
    search_input = None
    # special case: flag for @
    attag = False

    if request.method == 'GET':
        query_dict = request.GET
        search_input = query_dict.get('search_input')
    # filter all messages contain the word  or all users contain the word
    # search_input contains @ -> cut @ off and set flag
    # the reason behind this is we save username instead of @username, so if someone is looking for
    # @kps for example, we wont find him, because the database don't know him
    if search_input[0] == "#":
        hashtag(request, search_input)
    if search_input[0] == "@":
        attag = True
        search_input = search_input[1:]
    dbmessage_list = Message.objects.all().select_related('user__userprofile') \
        .filter(
        Q(text__contains=search_input) | Q(user__username__contains=search_input)
    ).order_by('-date')
    print(dbmessage_list)
    message_list = []
    for message in dbmessage_list:
        copy_message = copy.copy(message)
        message_list.append(dbm_to_m(copy_message))
    message_list = zip(message_list, dbmessage_list)

    user_list = User.objects.all() \
        .filter(Q(username__contains=search_input)
                | Q(first_name__contains=search_input)
                | Q(last_name__contains=search_input)
                )
    hashtag_list = Hashtag.objects.all().filter(Q(name__contains=search_input))
    # flag was set -> back to normal input
    if attag:
        search_input = '@'+search_input

    context = {
        'user_list': user_list,
        'search': 'Suchergebnisse f&uuml;r "' + search_input + '"',
        'hashtag_list': hashtag_list,
        'message_list': message_list,
        'active_page': 'index',
        'nav': Nav.nav,
        'msgForm': msgDialog(request),
    }
    return render(request, 'search.html', context)


# click on hashtaglinks will redirect to this function.
def hashtag(request, text):
    search_input = text

    # filter all messages contain #
    dbmessage_list = Message.objects.all().filter(hashtags__name=search_input).order_by('-date')
    message_list = []
    for message in dbmessage_list:
        copy_message = copy.copy(message)
        message_list.append(dbm_to_m(copy_message))
    message_list = zip(message_list, dbmessage_list)

    context = {
        'search': 'Beitr&auml;ge zum Thema "#' + search_input + '"',
        'message_list': message_list,
        'active_page': 'index',
        'is_hash': True,
        'nav': Nav.nav,
        'msgForm': msgDialog(request),
    }
    return render(request, 'search.html', context)