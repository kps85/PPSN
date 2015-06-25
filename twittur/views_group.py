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

    # initialize sidebar lists
    widgets = getWidgets(request)

    context = {
        'active_page': 'group', 'groupshort': groupshort, 'nav': Nav.nav,
        'new': widgets['new'], 'msgForm': widgets['msgForm'],
        'show_member': False, 'is_member': False,
        'hot_list': widgets['hot_list'], 'group_sb_list': widgets['group_sb_list'],
        'follow_sb_list': sorted(widgets['follow_list'], key=lambda x: random.random())[:5],
        'safetyLevels': widgets['safetyLevels']
    }

    # if message was sent to view: return success message
    if request.method == 'POST':
        context['success_msg'] = editMessage(request)

    group = GroupProfile.objects.get(short__exact=groupshort)
    context['group'] = group
    context['member_list'] = group.member.exclude(pk=group.admin.id).order_by('first_name')
    if request.user in context['member_list']:
        context['is_member'] = True
        if group.admin == request.user:
            context['button_text'] = '<span class="glyphicon glyphicon-cog"></span> ' + group.short.upper() + ' bearbeiten'
        else:
            context['button_text'] = '<span class="glyphicon glyphicon-log-out"></span> ' + group.short.upper() + ' verlassen'
    else:
        context['button_text'] = '<span class="glyphicon glyphicon-log-in"></span> ' + group.short.upper() + ' beitreten'

    if 'member' in request.GET:
        context['show_member'] = True

    messages = getMessages(data={'page': 'group', 'data': group, 'request': request})
    context['message_list'], context['has_msg'] = messages['message_list'], messages['has_msg']
    context['list_end'] = messages['list_end']

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
        'safetyLevels': widgets['safetyLevels']
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
    success_msg, error_msg, member_list = None, None, group.member.all()

    # check if user is group admin
    # if user is not group admin, redirect to group page
    if request.user != group.admin:
        return HttpResponseRedirect('/twittur/group/'+groupshort)

    # initialize sidebar lists
    widgets = getWidgets(request)

    context = {
        'active_page': 'settings', 'nav': Nav.nav, 'new': widgets['new'], 'msgForm': widgets['msgForm'],
        'success_msg': success_msg, 'error_msg': error_msg,
        'group': group, 'member_list': member_list,
        'safetyLevels': widgets['safetyLevels']
    }

    # else: validate GroupProfileEditForm and save changes
    if request.method == 'POST':
        # check if group should be deleted
        # if true: delete group, return to index
        if 'delete' in request.POST and request.POST['delete'] == 'true':
            group.delete()
            return HttpResponseRedirect('/twittur/')
        elif 'promUser' or 'remUser' in request.POST:
            context['success_msg'] = editMessage(request)
        else:
            gpeForm = GroupProfileEditForm(request.POST, request.FILES, instance=group)
            # if picture has changed, delete old picture
            # do not, if old picture was default picture
            if 'picture' in request.FILES or 'picture-clear' in request.POST:
                gpeForm.oldPicture = group.picture
                if gpeForm.oldPicture != 'picture/gdefault.gif':
                    gpeForm.oldPicture.delete()
            if gpeForm.is_valid():
                gpeForm.save()
                context['success_msg'] = 'Gruppendaten wurden erfolgreich aktualisiert.'
            else:
                # return errors if GroupProfileEditForm is not valid
                context['error_msg'] = gpeForm.errors

    # initialize GroupProfileEditForm with current groups information
    context['gpeForm'] = GroupProfileEditForm(instance=group)

    # return information to render settings.html
    return render(request, 'settings.html', context)
