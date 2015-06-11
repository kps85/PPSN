import copy

from django.db.models import Count, Q
from django.shortcuts import render

from .functions import dbm_to_m
from .models import Message, Nav, Hashtag
from .views import msgDialog
from django.contrib.auth.models import User


# search input
def search(request):
    search_input = None
    # special case: flag for @
    search_error = {}
    msgForm = msgDialog(request)
    hot_list = Hashtag.objects.annotate(hashtag_count=Count('hashtags__hashtags__name')) \
                       .order_by('-hashtag_count')[:5]
    follow_list = request.user.userprofile.follow.all()

    if request.method == 'GET':
        query_dict = request.GET
        search_input = query_dict.get('search_input').split(" ")

    if search_input is None or search_input == "":
        search_error["no_term"] = "Kein Suchbegriff eingegeben!"
        context_error = {
            'active_page': 'index',
            'nav': Nav.nav,
            'msgForm': msgForm,
            'error_msg': search_error
        }
        return render(request, 'index.html', context_error)

    # filter all messages contain the word  or all users contain the word
    # search_input contains @ -> cut @ off and set flag
    # the reason behind this is we save username instead of @username, so if someone is looking for
    # @kps for example, we wont find him, because the database don't know him

    message_list, user_list, hashtag_list = [], [], []

    for term in search_input:
        #print(term)
        attag = False
        if term[0] == "#":
            hashtag(request, term)
        elif term[0] == "@":
            attag = True
            term = term[1:]

        dbmessage_list = Message.objects.all().select_related('user__userprofile') \
            .filter(
            Q(text__contains=term) | Q(user__username__contains=term)
        ).order_by('-date')

        mList = []
        for message in dbmessage_list:
            copy_message = copy.copy(message)
            mList.append(dbm_to_m(copy_message))
        message_list.append(zip(mList, dbmessage_list))

        user_list.append(User.objects.all().filter(Q(username__contains=term)
                                            | Q(first_name__contains=term)
                                            | Q(last_name__contains=term)))

        hashtag_list.append(Hashtag.objects.all().filter(Q(name__contains=term)))

        # flag was set -> back to normal input
        if attag:
            term = '@' + term

    context = {
        'active_page': 'index',
        'nav': Nav.nav,
        'msgForm': msgForm,
        'hot_list': hot_list,
        'follow_list': follow_list,
        'search': 'Suchergebnisse f&uuml;r "' + ' '.join(search_input) + '"',
        'user_list': elimDups(user_list),
        'hashtag_list': elimDups(hashtag_list),
        'message_list': elimDups(message_list),
    }
    return render(request, 'search.html', context)


# click on hashtaglinks will redirect to this function.
def hashtag(request, text):
    msgForm = msgDialog(request)
    follow_list = request.user.userprofile.follow.all()
    hot_list = Hashtag.objects.annotate(hashtag_count=Count('hashtags__hashtags__name')) \
                       .order_by('-hashtag_count')[:5]

    # filter all messages contain #
    dbmessage_list = Message.objects.all().filter(hashtags__name=text).order_by('-date')
    message_list = []
    for message in dbmessage_list:
        copy_message = copy.copy(message)
        message_list.append(dbm_to_m(copy_message))
    message_list = zip(message_list, dbmessage_list)

    context = {
        'active_page': 'index',
        'nav': Nav.nav,
        'msgForm': msgForm,
        'hot_list': hot_list,
        'follow_list': follow_list,
        'search': 'Beitr&auml;ge zum Thema "#' + text + '"',
        'message_list': message_list,
        'is_hash': True,
    }
    return render(request, 'search.html', context)


# Entfernt Duplikate aus einer Liste und gibt die Liste ohne Duplikate zurück
def elimDups(list):
    dups, final = [], []
    for sub in list:
        for item in sub:
            if item in final: dups.append(item)
            else: final.append(item)
    return final
