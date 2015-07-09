# -*- coding: utf-8 -*-
"""
@package twittur
@author twittur-Team (Lilia B., Ming C., William C., Karl S., Thomas T., Steffen Z.)
Search Views
- SearchView:   a view for all search results
- HashtagView:  a view for a single topic
"""


import copy

from django.contrib.auth.models import User
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.core.exceptions import ObjectDoesNotExist

from .functions import dbm_to_m, elim_dups, get_context, get_messages
from .models import GroupProfile, Hashtag, Message
from .views import profile_view
from .views_group import group_view


# search input
def search_view(request):
    """
    displays all results for a specific search query
    :param request:
    :return: rendered HTML in template 'search.html'
    """

    if not request.user.is_authenticated():             # check if user is logged in
        return HttpResponseRedirect('/twittur/login/')  # if not -> redirect to FTU

    # initialize data dictionary 'context' with relevant display information
    context = get_context(request, 'search', request.user)

    if 'search_input' in request.GET:
        search_input = request.GET['search_input'].strip().split(" ")
    elif 'search_input' in request.POST:
        search_input = request.POST['search_input'].strip().split(" ")
    else:
        search_input = None
    context['search'] = 'Suchergebnisse f&uuml;r "<em>' + ' '.join(search_input) + '</em>"'
    context['search_input'] = ' '.join(search_input)
        
    if search_input is None or search_input[0] == "":
        context['no_input'] = 'So geht das aber nicht! Geben Sie ein Wort ein!'
        return render(request, 'search.html', context)

    # filter all messages contain the word  or all users contain the word
    # search_input contains @ -> cut @ off and set flag
    # the reason behind this is we save username instead of @username, so if someone is looking for
    # @kps for example, we wont find him, because the database don't know him

    user_list, group_list, hashtag_list, message_list = [], [], [], []
    messages = get_messages(data={'page': 'search', 'data': search_input, 'end': None, 'request': request})
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
        if len(search_input) == 1 and len(term) > 1:
            if term[0] == "#":
                try:
                    hashtag = Hashtag.objects.get(name__exact=term[1:])
                except ObjectDoesNotExist:
                    pass
                else:
                    return hashtag_view(request, hashtag.name)
            elif term[0] == "&":
                try:
                    group = GroupProfile.objects.get(short__exact=term[1:])
                except ObjectDoesNotExist:
                    pass
                else:
                    return group_view(request, group.short)
            elif term[0] == "@":
                try:
                    user = User.objects.get(username__exact=term[1:])
                except ObjectDoesNotExist:
                    pass
                else:
                    return profile_view(request, user.username)

        m_list, dbmessage_list, message_forms, comment_list, comment_count = [], [], [], [], []
        for message in messages_list:
            copy_message = copy.copy(message[1])
            m_list.append(dbm_to_m(copy_message))
            dbmessage_list.append(message[1])
            message_forms.append(message[2])
            comment_list.append(message[3])
            comment_count.append(message[4])

        m_zip = zip(m_list, dbmessage_list, message_forms, comment_list, comment_count)
        message_list.append(m_zip)
        if term[0] == '@' and len(term) > 1:
            user_list.append(User.objects.all().filter(Q(username__contains=term[1:])))
        elif term[0] == '@' and len(term) == 1:
            user_list.append(User.objects.all())
        else:
            user_list.append(User.objects.all().filter(Q(username__contains=term)))

        if term[0] == '&' and len(term) > 1:
            group = GroupProfile.objects.filter(Q(short__contains=term[1:]))
        elif term[0] == '&' and len(term) == 1:
            group = GroupProfile.objects.all()
        else:
            group = GroupProfile.objects.filter(Q(short__contains=term) | Q(name__contains=term))

        if len(group) > 0:
            group_list.append(group.distinct())

        if len(term) > 1 and term[0] == '#':
            hashtag = Hashtag.objects.all().filter(Q(name__contains=term[1:]))
        elif len(term) == 1 and term[0] == '#':
            hashtag = Hashtag.objects.all()
        else:
            hashtag = Hashtag.objects.all().filter(Q(name__contains=term))

        hashtag_count = []
        for item in hashtag:
            hashtag_count.append(Message.objects.filter(hashtags__name__exact=item.name).count())

        hashtag_list.append(zip(hashtag, hashtag_count))
    # eliminate duplicates from each list and sort message list by date
    user_list, hashtag_list = elim_dups(user_list), elim_dups(hashtag_list)
    group_list, message_list = elim_dups(group_list), elim_dups(message_list)
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
def hashtag_view(request, text):
    """
    displays messages which mentioned a specific topic (text)
    :param request:
    :param text: the topic
    :return: rendered HTML in template 'search.html'
    """

    if not request.user.is_authenticated():             # check if user is logged in
        return HttpResponseRedirect('/twittur/login/')  # if not -> redirect to FTU

    # initialize data dictionary 'context' with relevant display information
    context = get_context(request, 'hashtag', request.user)

    # if message was sent to view: return success message
    if request.method == 'POST':
        context['success_msg'] = 'Nachricht erfolgreich gesendet!'

    # Messages
    messages = get_messages(data={'page': 'hashtag', 'data': text, 'request': request})

    context['search'] = 'Beitr&auml;ge zum Thema "#' + text + '"'
    context['is_hash'], context['list_end'] = text, messages['list_end']
    context['message_list'], context['hash_list_length'] = messages['message_list'], messages['list_length']

    return render(request, 'search.html', context)
