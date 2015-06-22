import copy, random

from django.contrib.auth.models import User
from django.db.models import Q
from django.shortcuts import render

from .functions import dbm_to_m, editMessage, getMessages, getWidgets
from .models import GroupProfile, Hashtag, Nav


# search input
def search(request):
    # initialize varios information
    search_input, success_msg, error_msg, end, list_end = None, None, {}, 5, False

    # initialize sidebar lists
    widgets = getWidgets(request)

    # if message was sent to view: return success message
    if request.method == 'POST':
        success_msg = editMessage(request)

    if 'search_input' in request.GET:
        search_input = request.GET['search_input'].strip().split(" ")
    elif 'search_input' in request.POST:
        search_input = request.POST['search_input'].strip().split(" ")
    else:
        search_input = None

    print("test")
    if request.method == 'GET' and 'length' in request.GET:
        end = int(request.GET.get('length')) + 5

        # Messages
        messages = getMessages(data={'page': 'search', 'user': search_input, 'end': end, 'request': request})
        message_list = zip(
            messages['message_list'][:end], messages['dbmessage_list'][:end],
            messages['comment_list'], messages['comment_count']
        )

        context = {
            'active_page': 'search', 'user': request.user, 'msgForm': widgets['msgForm'],
            'search_input': ' '.join(search_input), 'message_list': message_list, 'list_end': messages['list_end']
        }
        return render(request, 'message_box_reload.html', context)
        
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
    messages = getMessages(data={'page': 'search', 'user': search_input, 'request': request})
    if len(messages['message_list']) <= end:
        list_end = True

    for term in search_input:
        # special case: flag for @
        attag = False
        if term[:1] == "#":
            hashtag(request, term)
        elif term[:1] == "@":
            attag = True
            term = term[1:]

        mList = []
        for message in messages['dbmessage_list']:
            copy_message = copy.copy(message)
            mList.append(dbm_to_m(copy_message))

        mZip = zip(mList, messages['dbmessage_list'], messages['comment_list'], messages['comment_count'])
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

    context = {
        'active_page': 'search', 'nav': Nav.nav, 'new': widgets['new'], 'msgForm': widgets['msgForm'],
        'success_msg': success_msg,
        'search': 'Suchergebnisse f&uuml;r "<em>' + ' '.join(search_input) + '</em>"',
        'search_input': ' '.join(search_input), 'list_end': list_end,
        'user_list': user_list, 'user_list_length': len(user_list),
        'group_list': group_list, 'group_list_length': len(group_list),
        'hashtag_list': hashtag_list, 'hashtag_list_length': len(hashtag_list),
        'message_list': message_list[:end], 'message_list_length': len(message_list),
        'hot_list': widgets['hot_list'], 'group_sb_list': widgets['group_sb_list'],
        'follow_sb_list': sorted(widgets['follow_list'], key=lambda x: random.random())[:5]
    }
    return render(request, 'search.html', context)


# click on hashtaglinks will redirect to this function.
def hashtag(request, text):
    success_msg, end = None, 5

    # initialize sidebar lists
    widgets = getWidgets(request)

    # if message was sent to view: return success message
    if request.method == 'POST':
        success_msg = editMessage(request)

    if request.method == 'GET' and 'length' in request.GET:
        end = int(request.GET.get('length')) + 5

    # Messages
    messages = getMessages(data={'page': 'hashtag', 'user': text, 'end': end, 'request': request})
    message_list = zip(
        messages['message_list'][:end], messages['dbmessage_list'][:end],
        messages['comment_list'], messages['comment_count']
    )

    if request.method == 'GET' and 'length' in request.GET:
        context = {'active_page': 'hashtag', 'user': request.user, 'msgForm': widgets['msgForm'],
                   'is_hash': text, 'message_list': message_list, 'list_end': messages['list_end']}
        return render(request, 'message_box_reload.html', context)

    context = {
        'active_page': 'hashtag', 'nav': Nav.nav, 'new': widgets['new'], 'msgForm': widgets['msgForm'],
        'success_msg': success_msg,
        'search': 'Beitr&auml;ge zum Thema "#' + text + '"', 'is_hash': text, 'list_end': messages['list_end'],
        'message_list': message_list, 'hash_list_length': len(messages['dbmessage_list']),
        'hot_list': widgets['hot_list'], 'group_sb_list': widgets['group_sb_list'],
        'follow_sb_list': sorted(widgets['follow_list'], key=lambda x: random.random())[:5],
    }
    return render(request, 'search.html', context)


# Entfernt Duplikate aus einer Liste und gibt die Liste ohne Duplikate zurueck
def elimDups(list):
    dups, final = [], []
    for sub in list:
        for item in sub:
            if item in final: dups.append(item)
            else: final.append(item)
    return final