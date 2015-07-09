"""
-*- coding: utf-8 -*-
@package twittur
@author twittur-Team (Lilia B., Ming C., William C., Karl S., Thomas T., Steffen Z.)
API Views
- message_get:
- message_set:
"""

import datetime

from django.db.models import Q
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.utils.html import mark_safe

from .forms import MessageForm
from .functions import create_abs_url, msg_to_db, pw_generator, verification_mail
from .models import GroupProfile, Message, User, UserProfile


def install_view(request):

    if len(User.objects.all()) != 0:
        return HttpResponseRedirect('/twittur/login/')

    context = {'active_page': 'install'}

    grp_list = [{
        'Name': 'TU Berlin', 'Short': 'tub',
        'SubGroups': [
            {'Name': mark_safe('Fakultät I'), 'Short': 'fak1', 'SubGroups': [
                {'Name': 'Kultur und Technik', 'Short': 'kut', 'Desc': ''}
            ]},
            {'Name': mark_safe('Fakultät II'), 'Short': 'fak2', 'SubGroups': [
                {'Name': 'Chemie', 'Short': 'chem', 'Desc': ''}
            ]},
            {'Name': mark_safe('Fakultät III'), 'Short': 'fak3', 'SubGroups': [
                {'Name': 'Biotechnologie', 'Short': 'bt', 'Desc': ''}
            ]},
            {'Name': mark_safe('Fakultät IV'), 'Short': 'fak4', 'SubGroups': [
                {'Name': 'Automotive Systems', 'Short': 'ausy', 'Desc': ''},
                {'Name': 'Computational Neuroscience', 'Short': 'coneuro', 'Desc': ''},
                {'Name': 'Elektrotechnik', 'Short': 'etech', 'Desc': ''},
                {'Name': 'ICT Innovation', 'Short': 'ict', 'Desc': ''},
                {'Name': 'Informatik', 'Short': 'inf', 'Desc': ''},
                {'Name': 'Medieninformatik', 'Short': 'minf', 'Desc': ''},
                {'Name': 'Technische Informatik', 'Short': 'tinf', 'Desc': ''},
                {'Name': 'Wirtschaftsinformatik', 'Short': 'winf', 'Desc': ''}
            ]},
            {'Name': mark_safe('Fakultät V'), 'Short': 'fak5', 'SubGroups': [
                {'Name': 'Maschinenbau', 'Short': 'mb', 'Desc': ''}
            ]},
            {'Name': mark_safe('Fakultät VI'), 'Short': 'fak6', 'SubGroups': [
                {'Name': 'Architektur', 'Short': 'arch', 'Desc': ''}
            ]},
            {'Name': mark_safe('Fakultät VII'), 'Short': 'fak7', 'SubGroups': [
                {'Name': 'Betriebswirtschaftslehre', 'Short': 'bwl', 'Desc': ''},
                {'Name': 'Economics', 'Short': 'be', 'Desc': ''},
                {'Name': 'Innovation Management and Entrepreneurship', 'Short': 'ime', 'Desc': ''},
                {'Name': 'Master of Industrial and Network Economics', 'Short': 'mine', 'Desc': ''},
                {'Name': 'Nachhaltiges Management', 'Short': 'nm', 'Desc': ''},
                {'Name': 'Volkswirtschaftslehre', 'Short': 'vwl', 'Desc': ''},
                {'Name': 'Wirtschaftsingenieurwesen', 'Short': 'wiing', 'Desc': ''}
            ]},
        ]
    }]

    if request.method == 'POST':
        username, password, email = "admin", request.POST['password'], request.POST['email']
        error_msg = None

        # EMail validation
        mail = email.split('@')
        if len(mail) == 1 or not (mail[1].endswith(".tu-berlin.de")
                                  or (email[(len(email) - 13):len(email)] == '@tu-berlin.de')):
            error_msg = "Keine g&uuml;ltige TU E-Mail Adresse!"
        else:
            if User.objects.filter(email=email).exists():
                error_msg = "Ein Benutzer mit dieser E-Mail Adresse existiert bereits!"


        # error?
        if error_msg:
            context['error_msg'] = error_msg
            return render(request, 'install.html', context)

        # if data is correct -> create User and Userprofile
        user = User.objects.create_user(username, email, password)
        user.is_active = False
        user.is_superuser = True
        user.is_staff = True

        # Hash for verification
        new_hash = pw_generator(hashed=True)
        user_profile = UserProfile(userprofile=user, location="Irgendwo", verifyHash=new_hash)
        verification_mail(request, user)
        user.save()
        user_profile.save()

        for grp in grp_list:
            name, short = grp['Name'], grp['Short']
            if not GroupProfile.objects.filter(short=short).exists():
                group = GroupProfile(
                    name=name, short=short, admin=user, date=datetime.datetime.now(),
                    joinable=False
                )
                group.save()
                group.member.add(user)
            for sub_grp in grp['SubGroups']:
                sub_name, sub_short = sub_grp['Name'], sub_grp['Short']
                if not GroupProfile.objects.filter(short=sub_short).exists():
                    sub_group = GroupProfile(
                        name=sub_name, short=sub_short, admin=user, date=datetime.datetime.now(),
                        joinable=False, supergroup=group
                    )
                    sub_group.save()
                    sub_group.member.add(user)
                for sub_sub in sub_grp['SubGroups']:
                    s_sub_name, s_sub_short = sub_sub['Name'], sub_sub['Short']
                    if not GroupProfile.objects.filter(short=s_sub_short).exists():
                        sub_sub_group = GroupProfile(
                            name=s_sub_name, short=s_sub_short, admin=user, date=datetime.datetime.now(),
                            joinable=False, supergroup=sub_group
                        )
                        sub_sub_group.save()
                        sub_sub_group.member.add(user)

        group = GroupProfile.objects.get(short='inf')
        user_profile.academicDiscipline = group.name
        user_profile.save()

        return HttpResponseRedirect('/twittur/install/')

    return render(request, 'install.html', context)


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

