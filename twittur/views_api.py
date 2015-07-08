"""
-*- coding: utf-8 -*-
@package twittur
@author twittur-Team (Lilia B., Ming C., William C., Karl S., Thomas T., Steffen Z.)
API Views
- message_get:
- message_set:
"""

from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import render

from .forms import MessageForm
from .functions import create_abs_url, msg_to_db
from .models import Message, User


def message_get(request):

    p_user = User.objects.get(username=request.GET['user'].lower())
    p_hash = p_user.userprofile.verifyHash
    context = {'message_list': []}

    if p_hash == request.GET['hash']:
        messages = Message.objects.filter(
            Q(user=p_user) & Q(group=None) & Q(attags=None) & Q(comment=None) & Q(ignore=False)
        ).order_by('-date')
        for msg in messages:
            msg.url = create_abs_url(request, 'message', msg.id)
            context['message_list'].append(msg)

    return render(request, "message_list.xml", context)


def message_set(request, user, hash_item):

    p_user = User.objects.get(username=user.lower())
    p_hash = p_user.userprofile.verifyHash

    if p_hash == hash_item:
        msg_form = MessageForm(request.POST, request.FILES, user_id=p_user.id)
        if msg_form.is_valid():
            msg_form.save()
            msg_to_db(msg_form.instance)
        return HttpResponse("Nachricht erfolgreich gesendet!")
    else:
        return HttpResponse("Nachricht nicht gesendet!")

