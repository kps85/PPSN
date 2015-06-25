import copy, random

from django.contrib.auth.models import User
from django.db.models import Q
from django.shortcuts import render

from .functions import dbm_to_m, elimDups, getMessages, getWidgets
from .models import GroupProfile, Hashtag, Nav


# search input
def search(request):
    # initialize varios information
    success_msg, error_msg = None, {}

    # initialize sidebar lists
    widgets = getWidgets(request)

    context = {
        'active_page': 'search', 'nav': Nav.nav, 'new': widgets['new'], 'msgForm': widgets['msgForm'],
        'list_end': 5,
        'hot_list': widgets['hot_list'], 'group_sb_list': widgets['group_sb_list'],
        'follow_sb_list': sorted(widgets['follow_list'], key=lambda x: random.random())[:5]
    }

    if 'search_input' in request.GET:
        search_input = request.GET['search_input'].strip().split(" ")
    elif 'search_input' in request.POST:
        search_input = request.POST['search_input'].strip().split(" ")
    else:
        search_input = None
    context['search'] = 'Suchergebnisse f&uuml;r "<em>' + ' '.join(search_input) + '</em>"'
    context['search_input'] = ' '.join(search_input)
        
    if search_input is None or search_input[0] == "":
        error_msg["no_term"] = "Kein Suchbegriff eingegeben!"
        context_error = {
            'active_page': 'index', 'nav': Nav.nav, 'new': widgets['new'], 'msgForm': widgets['msgForm'],
            'error_msg': error_msg,
            'hot_list': widgets['hot_list'], 'group_sb_list': widgets['group_sb_list'],
            'follow_sb_list': sorted(widgets['follow_list'], key=lambda x: random.random())[:5]
        }
        return render(request, 'index.html', context_error)

    # filter all messages contain the word  or all users contain the word
    # search_input contains @ -> cut @ off and set flag
    # the reason behind this is we save username instead of @username, so if someone is looking for
    # @kps for example, we wont find him, because the database don't know him

    user_list, group_list, hashtag_list, message_list = [], [], [], []
    messages = getMessages(data={'page': 'search', 'data': search_input, 'end': None, 'request': request})
    messages_list = list(messages['message_list'])

    if messages['list_length'] <= context['list_end']:
        context['list_end'] = True
        if len(messages_list) <= 5:
            context['sListEnd'] = 5

    # if message was sent to view: return success message
    if request.method == 'POST':
        context['success_msg'] = 'Nachricht erfolgreich gesendet!'
        context['list_end'] = int(request.POST['list_end'])

    for term in search_input:
        # special case: flag for @
        attag = False
        if term[:1] == "#":
            hashtag(request, term)
        elif term[:1] == "@":
            attag = True
            term = term[1:]

        mList, dbmessage_list, comment_list, comment_count = [], [], [], []
        for message in messages_list:
            copy_message = copy.copy(message[1])
            mList.append(dbm_to_m(copy_message))
            dbmessage_list.append(message[1])
            comment_list.append(message[2])
            comment_count.append(message[3])

        mZip = zip(mList, dbmessage_list, comment_list, comment_count)
        message_list.append(mZip)

        user_list.append(User.objects.all().filter(Q(username__contains=term)
                                            | Q(first_name__contains=term)
                                            | Q(last_name__contains=term)))

        group = GroupProfile.objects.filter(Q(short__contains=term) | Q(name__contains=term) | Q(desc__contains=term))
        if len(group) > 0:
            group_list.append(group)

        hashtag_list.append(Hashtag.objects.all().filter(Q(name__contains=term)))

        # flag was set -> back to normal input
        if attag:
            term = '@' + term

    user_list = elimDups(user_list)
    hashtag_list = elimDups(hashtag_list)
    message_list = elimDups(message_list)
    message_list.sort(key=lambda x: x[0].date, reverse=True)

    context['user_list'], context['user_list_length'] = user_list, len(user_list)
    context['group_list'], context['group_list_length'] = group_list, len(group_list)
    context['hashtag_list'], context['hashtag_list_length'] = hashtag_list, len(hashtag_list)
    context['message_list_length'] = messages['list_length']

    if 'sListEnd' in context:
        context['message_list'] = message_list[:context['sListEnd']]
    else:
        context['message_list'] = message_list[:context['list_end']]

    return render(request, 'search.html', context)


# click on hashtaglinks will redirect to this function.
def hashtag(request, text):
    success_msg, end = None, 5

    # initialize sidebar lists
    widgets = getWidgets(request)

    # if message was sent to view: return success message
    if request.method == 'POST':
        success_msg = 'Nachricht erfolgreich gesendet!'

    # Messages
    messages = getMessages(data={'page': 'hashtag', 'data': text, 'request': request})

    context = {
        'active_page': 'hashtag', 'nav': Nav.nav, 'new': widgets['new'], 'msgForm': widgets['msgForm'],
        'success_msg': success_msg,
        'search': 'Beitr&auml;ge zum Thema "#' + text + '"', 'is_hash': text, 'list_end': messages['list_end'],
        'message_list': messages['message_list'], 'hash_list_length': messages['list_length'],
        'hot_list': widgets['hot_list'], 'group_sb_list': widgets['group_sb_list'],
        'follow_sb_list': sorted(widgets['follow_list'], key=lambda x: random.random())[:5],
    }
    return render(request, 'search.html', context)