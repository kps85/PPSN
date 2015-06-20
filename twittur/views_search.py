import copy

from django.contrib.auth.models import User
from django.db.models import Count, Q
from django.shortcuts import render

from .functions import dbm_to_m, getMessages
from .models import GroupProfile, Hashtag, Message, Nav, UserProfile
from .views import msgDialog


# search input
def search(request):

    search_input, search_error, msgForm, end, list_end = None, {}, msgDialog(request), 5, False

    # Follow List
    curUser = UserProfile.objects.get(userprofile=request.user)
    follow_list = curUser.follow.all()
    # Group List
    group_sb_list = GroupProfile.objects.all().filter(Q(member__exact=request.user))
    # Beliebte Themen
    hot_list = Hashtag.objects.annotate(hashtag_count=Count('hashtags__hashtags__name')) \
                   .order_by('-hashtag_count')[:5]

    if request.method == 'GET':
        search_input = request.GET['search_input'].strip().split(" ")

    if request.method == 'GET' and 'last' in request.GET:
        last = Message.objects.get(id=request.GET.get('last'))

        for term in search_input:
            if term[:1] == "#" or term[:1] == "@":
                term = term[1:]
            messages = Message.objects.filter(
                Q(text__contains=term) | Q(user__username__contains=term)
            ).order_by('-date')
            for item in messages:
                if item == last:
                    break
                end += + 1
        end += 6

        # Messages
        msgForm = msgDialog(request)
        messages = getMessages('search', search_input, end)
        message_list = zip(messages['message_list'], messages['dbmessage_list'], messages['comment_list'])

        if end > len(messages['message_list']):
            list_end = True

        context = {'active_page': 'search', 'user': request.user, 'list_end': list_end,
                   'search_input': ' '.join(search_input), 'message_list': message_list, 'msgForm': msgForm}
        return render(request, 'message_box_reload.html', context)
        
    if search_input is None or search_input[0] == "":
        search_error["no_term"] = "Kein Suchbegriff eingegeben!"
        context_error = {
            'active_page': 'index',
            'nav': Nav.nav,
            'msgForm': msgForm,
            'error_msg': search_error,
            'hot_list': hot_list,
            'follow_list': follow_list,
            'group_sb_list': group_sb_list,
        }
        return render(request, 'index.html', context_error)

    # filter all messages contain the word  or all users contain the word
    # search_input contains @ -> cut @ off and set flag
    # the reason behind this is we save username instead of @username, so if someone is looking for
    # @kps for example, we wont find him, because the database don't know him

    user_list, group_list, hashtag_list, message_list = [], [], [], []

    for term in search_input:
        # special case: flag for @
        attag = False
        if term[:1] == "#":
            hashtag(request, term)
        elif term[:1] == "@":
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

    context = {
        'active_page': 'index',
        'nav': Nav.nav,
        'msgForm': msgForm,
        'hot_list': hot_list,
        'follow_list': follow_list,
        'group_sb_list': group_sb_list,
        'search': 'Suchergebnisse f&uuml;r "<em>' + ' '.join(search_input) + '</em>"',
        'search_input': ' '.join(search_input),
        'user_list': user_list,
        'user_list_length': len(user_list),
        'group_list': group_list,
        'group_list_length': len(group_list),
        'hashtag_list': hashtag_list,
        'hashtag_list_length': len(hashtag_list),
        'message_list': message_list[:end],
        'message_list_length': len(message_list),
    }
    return render(request, 'search.html', context)


# click on hashtaglinks will redirect to this function.
def hashtag(request, text):
    msgForm, end = msgDialog(request), 5

    # Follow List
    curUser = UserProfile.objects.get(userprofile=request.user)
    follow_list = curUser.follow.all()
    # Group List
    group_sb_list = GroupProfile.objects.all().filter(Q(member__exact=request.user))
    # Beliebte Themen
    hot_list = Hashtag.objects.annotate(hashtag_count=Count('hashtags__hashtags__name')) \
                   .order_by('-hashtag_count')[:5]

    if request.method == 'GET' and 'last' in request.GET:
        last = Message.objects.get(id=request.GET.get('last'))
        messages = Message.objects.filter(hashtags__name=text).order_by('-date')
        for item in messages:
            if item == last:
                break
            end += + 1
        end += 6

        # Messages
        msgForm = msgDialog(request)
        messages = getMessages('hashtag', text, end)
        message_list = zip(messages['message_list'], messages['dbmessage_list'], messages['comment_list'])

        if end > len(messages['message_list']):
            list_end = True

        context = {'active_page': 'hashtag', 'user': request.user, 'list_end': list_end,
                   'is_hash': text, 'message_list': message_list, 'msgForm': msgForm}
        return render(request, 'message_box_reload.html', context)

    # Messages
    msgForm = msgDialog(request)
    messages = getMessages('hashtag', text, end)
    message_list = zip(messages['message_list'], messages['dbmessage_list'], messages['comment_list'])

    context = {
        'active_page': 'index',
        'nav': Nav.nav,
        'msgForm': msgForm,
        'hot_list': hot_list,
        'follow_list': follow_list,
        'group_sb_list': group_sb_list,
        'search': 'Beitr&auml;ge zum Thema "#' + text + '"',
        'message_list': message_list,
        'hash_list_length': len(messages['dbmessage_list']),
        'is_hash': text,
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
