import random, re

from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render

from .forms import GroupProfileForm, GroupProfileEditForm
from .functions import editMessage, getWidgets, setNotification, getMessages
from .models import GroupProfile, Nav


def group(request, groupshort):
    # check if user is logged in
    # if user is not logged in, redirect to FTU
    if not request.user.is_authenticated():
        return HttpResponseRedirect('/twittur/login/')

    # initialize various information
    show_member, is_member, button_text, success_msg = False, False, None, None

    # initialize sidebar lists
    widgets = getWidgets(request)

    # if message was sent to view: return success message
    if request.method == 'POST':
        success_msg = editMessage(request)


    group = GroupProfile.objects.get(short__exact=groupshort)
    member_list = group.member.order_by('first_name')
    if request.user in member_list:
        is_member = True
        if group.admin == request.user:
            button_text = '<span class="glyphicon glyphicon-log-out"></span> ' + group.short.upper() + ' bearbeiten'
        else:
            button_text = '<span class="glyphicon glyphicon-log-out"></span> ' + group.short.upper() + ' verlassen'
    else:
        button_text = '<span class="glyphicon glyphicon-log-in"></span> ' + group.short.upper() + ' beitreten'

    if 'member' in request.GET:
        show_member = True

    end = 5
    messages = getMessages(data={'page': 'group', 'user': None, 'group': group, 'end': end, 'request': request})
    message_list = zip(
        messages['message_list'][:end], messages['dbmessage_list'][:end],
        messages['comment_list'], messages['comment_count']
    )
    print(messages['has_msg'])
    context = {
        'active_page': 'group', 'groupshort': groupshort, 'nav': Nav.nav, 'new': widgets['new'], 'msgForm': widgets['msgForm'],
        'group': group, 'member_list': member_list, 'is_member': is_member, 'button_text': button_text,
        'show_member': show_member, 'success_msg': success_msg, 'message_list': message_list, 'has_msg': messages['has_msg'],
        'hot_list': widgets['hot_list'], 'group_sb_list': widgets['group_sb_list'],
        'follow_sb_list': sorted(widgets['follow_list'], key=lambda x: random.random())[:5]
    }
    return render(request, 'profile.html', context)

# view for add a new group
def addgroup(request):
    # check if user is logged in
    # if user is not logged in, redirect to FTU
    if not request.user.is_authenticated():
        return HttpResponseRedirect('/twittur/login/')

    data, errors, error_msg = {}, {}, {}
    group_list = GroupProfile.objects.all()

    # initialize sidebar lists
    widgets = getWidgets(request)

    if request.POST:
        groupProfileForm = GroupProfileForm(request.POST)
        if groupProfileForm.is_valid():
            try:
                GroupProfile.objects.get(name__exact=groupProfileForm.instance.name)
            except ObjectDoesNotExist:
                # case if group short is available
                for group in group_list:
                    if request.POST.get('short').lower() == group.short.lower():
                        errors['error_groupshort'] = "Sorry, Gruppenabk&uuml;rzung ist bereits vergeben."
                if 'error_groupshort' not in errors:
                    if re.match("^[a-zA-Z0-9-_.]*$", request.POST.get('short')) is None:
                        errors['error_groupshort'] = \
                            "Nur 'A-Z, a-z, 0-9, -, _' und '.' in der Gruppenabk&uuml;rzung erlaubt!"
                if request.POST.get('password') != request.POST.get('ack_password'):
                    errors['error_grouppassword'] = "Passw&ouml;rter sind nicht gleich!"
                if len(errors) == 0:
                    groupProfileForm.instance.groupprofile = groupProfileForm.instance
                    groupProfileForm.instance.admin = request.user
                    groupProfileForm.save()
                    groupProfileForm.instance.member.add(request.user)

                    return HttpResponseRedirect('/twittur/group/' + groupProfileForm.instance.short)
            else:
                errors['error_groupname'] = "Gruppenname ist schon vergeben!"
            error_msg['data_invalid'] = 'Die eingegebenen Daten enthalten Fehler.'
    else:
        groupProfileForm = GroupProfileForm()

    context = {
        'active_page': 'group', 'nav': Nav.nav, 'new': widgets['new'], 'msgForm': widgets['msgForm'],
        'errors': errors, 'error_msg': error_msg,
        'groupProfileForm': groupProfileForm,
        'hot_list': widgets['hot_list'], 'group_sb_list': widgets['group_sb_list'],
        'follow_sb_list': sorted(widgets['follow_list'], key=lambda x: random.random())[:5],
    }
    return render(request, 'addgroup.html', context)


# function for delete/join/leave group
def djlgroup(request, groupshort):
    # Be sure this is the right function, true -> get group object
    if 'delete_join_group' in request.POST:
        group = GroupProfile.objects.get(short__exact=groupshort)
        admin = group.admin

        # Member function:
        # check if user is in group or not
        try:
            group.member.get(username__exact=request.user.username)
        # User does not exist, means he is not in group -> add him (password required?) -> redirect to groupsite
        except ObjectDoesNotExist:
            if 'joinWithPassword' in request.POST:
                if group.password == request.POST.get('password'):
                    group.member.add(request.user)
                else:
                    return HttpResponse("Falsches Passwort!")
            else:
                group.member.add(request.user)
            note = request.user.username + ' ist deiner Gruppe beigetreten.'
        # User exists -> delete him from group
        else:
            group.member.remove(request.user)
            note = request.user.username + ' hat deine Gruppe verlassen.'
        setNotification('group', data={'group': group, 'member': admin, 'note': note})

    return HttpResponseRedirect('/twittur/group/'+groupshort)


# TODO
# - Sichtbarkeit von Nachrichten? (Passwort required oder nicht)


# Page: 'Gruppen Einstellungen'
# - allows: editing editable group information and deleting group
# -- Name, Beschreibung
# - template: settings_group.html
def groupSettings(request, groupshort):
    # check if user is logged in
    # if user is not logged in, redirect to FTU
    if not request.user.is_authenticated():
        return HttpResponseRedirect('/twittur/login/')

    # get current groups information and initialize return messages
    group = GroupProfile.objects.get(short__exact=groupshort)
    success_msg, error_msg = None, None

    # check if user is group admin
    # if user is not group admin, redirect to group page
    if request.user != group.admin:
        return HttpResponseRedirect('/twittur/group/'+groupshort)

    # initialize sidebar lists
    widgets = getWidgets(request)

    # check if group should be deleted
    # if true: delete group, return to index
    if request.method == 'POST' and request.POST['delete'] == 'true':
        group.delete()
        return HttpResponseRedirect('/twittur/')
    # else: validate GroupProfileEditForm and save changes
    elif request.method == 'POST':
        gpeForm = GroupProfileEditForm(request.POST, request.FILES, instance=group)
        # if picture has changed, delete old picture
        # do not, if old picture was default picture
        if 'picture' in request.FILES or 'picture-clear' in request.POST:
            gpeForm.oldPicture = group.picture
            if gpeForm.oldPicture != 'picture/gdefault.gif':
                gpeForm.oldPicture.delete()
        if gpeForm.is_valid():
            gpeForm.save()
            success_msg = 'Gruppendaten wurden erfolgreich aktualisiert.'
        else:
            # return errors if GroupProfileEditForm is not valid
            error_msg = gpeForm.errors

    # initialize GroupProfileEditForm with current groups information
    gpeForm = GroupProfileEditForm(instance=group)

    # return relevant information to render settings.html
    context = {
        'active_page': 'settings', 'nav': Nav.nav, 'new': widgets['new'], 'msgForm': widgets['msgForm'],
        'success_msg': success_msg, 'error_msg': error_msg,
        'group': group,
        'gpeForm': gpeForm,
    }
    return render(request, 'settings.html', context)
