import re

from django.contrib.auth.hashers import check_password, make_password
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponseRedirect
from django.shortcuts import render

from .forms import GroupProfileForm, GroupProfileEditForm
from .functions import editMessage, getContext, getMessages, setNotification
from .models import GroupProfile


def GroupView(request, groupshort):
    # check if user is logged in
    # if user is not logged in, redirect to FTU
    if not request.user.is_authenticated():
        return HttpResponseRedirect('/twittur/login/')

    context = getContext(request, 'group', request.user)
    context['groupshort'] = groupshort.lower()

    # if message was sent to view: return success message
    if request.method == 'POST':
        if 'delete_join_group' in request.POST:
            context['error_msg'] = {'error_pw': 'Falsches Passwort eingegeben!'}
        else:
            context['success_msg'] = editMessage(request)

    try:
        group = GroupProfile.objects.get(short__contains=context['groupshort'])
        context['group'] = group
        context['member_list'] = group.member.exclude(pk=group.admin.id).order_by('first_name')
        if request.user in group.member.all():
            context['is_member'] = True
            if group.admin == request.user:
                context['button_text'] = '<span class="glyphicon glyphicon-cog"></span> ' \
                                         + group.short.upper() + ' bearbeiten'
            else:
                context['button_text'] = '<span class="glyphicon glyphicon-log-out"></span> ' \
                                         + group.short.upper() + ' verlassen'
        else:
            context['button_text'] = '<span class="glyphicon glyphicon-log-in"></span> ' \
                                     + group.short.upper() + ' beitreten'

        if 'member' in request.GET and request.user in group.member.all():
            context['show_member'] = True

        messages = getMessages(data={'page': 'group', 'data': group, 'request': request})
        context['message_list'], context['has_msg'] = messages['message_list'], messages['has_msg']
        context['list_end'] = messages['list_end']
    except:
        context['error_msg'] = {'error_group': 'Keine Gruppe mit der Abk&uuml;rzung '
                                               + context['groupshort'] + ' gefunden!'}

    return render(request, 'profile.html', context)


# view for add a new group
def GroupAddView(request):
    # check if user is logged in
    # if user is not logged in, redirect to FTU
    if not request.user.is_authenticated():
        return HttpResponseRedirect('/twittur/login/')

    context = getContext(request, 'group', request.user)

    if request.method == 'POST':
        dict = request.POST
        groupProfileForm = GroupProfileForm(dict)
        if groupProfileForm.is_valid():
            error_msg = {}
            try:
                GroupProfile.objects.get(name__exact=groupProfileForm.instance.name)
            except ObjectDoesNotExist:
                # case if group short is available
                group_list = GroupProfile.objects.all()
                for group in group_list:
                    if dict['short'].lower() == group.short.lower():
                        error_msg['error_groupshort'] = "Sorry, Gruppenabk&uuml;rzung ist bereits vergeben."
                if 'error_groupshort' not in error_msg:
                    if re.match("^[a-zA-Z0-9-_.]*$", dict['short']) is None:
                        error_msg['error_groupshort'] = \
                            "Nur 'A-Z, a-z, 0-9, -, _' und '.' in der Gruppenabk&uuml;rzung erlaubt!"
                if dict['password'] != dict['ack_password']:
                    error_msg['error_grouppassword'] = "Passw&ouml;rter sind nicht gleich!"
                if len(error_msg) == 0:
                    groupProfileForm.instance.groupprofile = groupProfileForm.instance
                    groupProfileForm.instance.admin = request.user
                    if groupProfileForm.instance.password != '':
                        groupProfileForm.instance.password = make_password(groupProfileForm.instance.password)
                    groupProfileForm.save()
                    groupProfileForm.instance.member.add(request.user)
                    return HttpResponseRedirect('/twittur/group/' + groupProfileForm.instance.short)
            else:
                error_msg['error_groupname'] = "Gruppenname ist schon vergeben!"
            context['error_msg'] = error_msg
    else:
        groupProfileForm = GroupProfileForm()
    context['groupProfileForm'] = groupProfileForm
    return render(request, 'addgroup.html', context)


# function for delete/join/leave group
def djlgroup(request, groupshort):

    if not request.user.is_authenticated():
        return HttpResponseRedirect('/twittur/login/')

    # Be sure this is the right function, true -> get group object
    if 'delete_join_group' in request.POST:
        group = GroupProfile.objects.get(short__exact=groupshort)
        admin, dict = group.admin, request.POST

        # Member function:
        # check if user is in group or not
        try:
            group.member.get(username__exact=request.user.username)
        # User does not exist, means he is not in group -> add him (password required?) -> redirect to groupsite
        except ObjectDoesNotExist:
            if dict['delete_join_group'] == 'join_pw':
                if check_password(dict['password'], group.password):
                    group.member.add(request.user)
                else:
                    return GroupView(request, groupshort)
            else:
                group.member.add(request.user)
            note = request.user.username + ' ist deiner Gruppe beigetreten.'
        # User exists -> delete him from group
        else:
            group.member.remove(request.user)
            note = request.user.username + ' hat deine Gruppe verlassen.'
        setNotification('group', data={'group': group, 'member': admin, 'note': note})

    return HttpResponseRedirect('/twittur/group/'+groupshort)


# Page: 'Gruppen Einstellungen'
# - allows: editing editable group information and deleting group
# -- Name, Beschreibung
# - template: settings_group.html
def GroupSettingsView(request, groupshort):
    # check if user is logged in
    # if user is not logged in, redirect to FTU
    if not request.user.is_authenticated():
        return HttpResponseRedirect('/twittur/login/')

    # get current groups information and initialize return messages
    group = GroupProfile.objects.get(short__exact=groupshort)

    # check if user is group admin
    # if user is not group admin, redirect to group page
    if request.user != group.admin:
        return HttpResponseRedirect('/twittur/group/'+groupshort)

    context = getContext(request, 'settings', request.user)
    context['group'], context['member_list'] = group, group.member.all()

    # else: validate GroupProfileEditForm and save changes
    if request.method == 'POST':
        # check if group should be deleted
        # if true: delete group, return to index
        if request.POST['delete'] == 'true':
            group.delete()
            return HttpResponseRedirect('/twittur/')
        elif any(item in request.POST for item in ['promUser', 'remUser']):
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
