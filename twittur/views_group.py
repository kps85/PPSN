# -*- coding: utf-8 -*-
"""
-*- coding: utf-8 -*-
@package twittur
@author twittur-Team (Lilia B., Ming C., William C., Karl S., Thomas T., Steffen Z.)
Group Views
- GroupView:            view for a single group
- GroupAddView:         view for group creation
- GroupSettingsView:    view for group settings
"""

import re

from django.contrib.auth.hashers import check_password, make_password
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponseRedirect
from django.shortcuts import render

from .forms import GroupProfileForm, GroupProfileEditForm
from .functions import get_context, get_messages, set_notification
from .models import User, GroupProfile


# Page: "Gruppe"
def group_view(request, groupshort):
    """

    :param request:
    :param groupshort:
    :return:
    """

    if not request.user.is_authenticated():             # check if user is logged in
        return HttpResponseRedirect('/twittur/login/')  # if user is not logged in, redirect to FTU

    # initialize data dictionary 'context' with relevant display information
    context = get_context(request, 'group', request.user)
    context['groupshort'] = groupshort.lower()

    try:
        group = GroupProfile.objects.get(short__exact=context['groupshort'])
        context['group'] = group
        context['member_list'] = group.member.exclude(pk=group.admin.id).order_by('first_name')

        # if message was sent to view: return success message
        if request.method == 'POST':
            if 'delete_join_group' in request.POST:
                context['error_msg'] = {'error_pw': 'Falsches Passwort eingegeben!'}
            elif 'promUser' in request.POST:
                member = User.objects.get(pk=request.POST['promUser'])
                set_notification('group_admin', data={'group': group, 'member': member})
                group.admin = member
                group.save()
                context['success_msg'] = "Mitglied erfolgreich befördert."
            elif 'remUser' in request.POST:
                member = User.objects.get(pk=request.POST['remUser'])
                set_notification('group', data={'group': group, 'member': member})
                group.member.remove(member)
                context['success_msg'] = "Mitglied erfolgreich entfernt."
            else:
                context['success_msg'] = 'Nachricht erfolgreich gesendet!'
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

        messages = get_messages(data={'page': 'group', 'data': group, 'request': request})
        context['message_list'], context['has_msg'] = messages['message_list'], messages['has_msg']
        context['list_end'] = messages['list_end']
    except ObjectDoesNotExist as e:
        context = get_context(request, '404', user=request.user)
        context['error_type'] = 'ObjectDoesNotExist'
        context['error_site'] = 'Gruppenseite'
        context['error_object'] = groupshort
        return render(request, '404.html', context)

    return render(request, 'profile.html', context)


# Page: "Gruppe hinzufuegen"
def group_add_view(request):
    """
    view for creating a new group
    :param request:
    :return:
    """

    if not request.user.is_authenticated():             # check if user is logged in
        return HttpResponseRedirect('/twittur/login/')  # if user is not logged in, redirect to FTU

    # initialize data dictionary 'context' with relevant display information
    context = get_context(request, 'group', request.user)

    if request.method == 'POST':
        group_profile_form = GroupProfileForm(request.POST)
        if group_profile_form.is_valid():
            group_profile_form.instance.groupprofile = group_profile_form.instance
            group_profile_form.instance.admin = request.user
            if group_profile_form.instance.password != '':
                group_profile_form.instance.password = make_password(group_profile_form.instance.password)
            group_profile_form.save()
            group_profile_form.instance.member.add(request.user)
            return HttpResponseRedirect('/twittur/group/' + group_profile_form.instance.short)
    else:
        group_profile_form = GroupProfileForm()
    context['groupProfileForm'] = group_profile_form
    return render(request, 'addgroup.html', context)


def djlgroup(request, groupshort):
    """
    function for delete/join/leave a group
    :param request:
    :param groupshort: the abbreviation of the group
    :return:
    """

    if not request.user.is_authenticated():             # check if user is logged in
        return HttpResponseRedirect('/twittur/login/')  # if user is not logged in, redirect to FTU

    # Be sure this is the right function, true -> get group object
    if 'delete_join_group' in request.POST:
        try:
            group = GroupProfile.objects.get(short__exact=groupshort)
        except ObjectDoesNotExist:
            context = get_context(request, '404', user=request.user)
            context['error_type'] = 'ObjectDoesNotExist'
            context['error_site'] = 'Gruppenseite'
            context['error_object'] = groupshort
            return render(request, '404.html', context)
        else:
            admin, data_dict = group.admin, request.POST

            # Member function:
            # check if user is in group or not
            try:
                group.member.get(username__exact=request.user.username)
            # User does not exist, means he is not in group -> add him (password required?) -> redirect to groupsite
            except ObjectDoesNotExist:
                if data_dict['delete_join_group'] == 'join_pw':
                    if check_password(data_dict['password'], group.password):
                        group.member.add(request.user)
                    else:
                        return group_view(request, groupshort)
                else:
                    group.member.add(request.user)
                note = request.user.username + ' ist deiner Gruppe beigetreten.'
            # User exists -> delete him from group
            else:
                group.member.remove(request.user)
                note = request.user.username + ' hat deine Gruppe verlassen.'
            set_notification('group', data={'group': group, 'member': admin, 'note': note})

        return HttpResponseRedirect('/twittur/group/'+groupshort)


# Page: "Gruppen Einstellungen"
def group_settings_view(request, groupshort):
    """
    settings page for groups
    can edit several information, remove and promote users and delete the whole group
    :param request:
    :param groupshort: the abbreviation of the group
    :return: rendered HTML in template 'settings.html'
    """

    if not request.user.is_authenticated():             # check if user is logged in
        return HttpResponseRedirect('/twittur/login/')  # if user is not logged in, redirect to FTU

    # get current groups information and initialize return messages
    try:
        group = GroupProfile.objects.get(short__exact=groupshort)
    except ObjectDoesNotExist:
        context = get_context(request, '404', user=request.user)
        context['error_type'] = 'ObjectDoesNotExist'
        context['error_site'] = 'Gruppenseite'
        context['error_object'] = groupshort
        return render(request, '404.html', context)

    else:
        if request.user != group.admin:                                 # check if user is group admin
            return HttpResponseRedirect('/twittur/group/'+groupshort)   # if not -> redirect to group page
        # initialize data dictionary 'context' with relevant display information
        context = get_context(request, 'settings', request.user)
        context['group'], context['member_list'] = group, group.member.all()

        # initialize GroupProfileEditForm with current groups information
        context['gpeForm'] = GroupProfileEditForm(instance=group)

        # else: validate GroupProfileEditForm and save changes
        if request.method == 'POST':
            # check if group should be deleted
            # if true: delete group, return to index
            if 'delete' in request.POST and request.POST['delete'] == 'true':
                group.delete()
                return HttpResponseRedirect('/twittur/')
            elif any(item in request.POST for item in ['promUser', 'remUser']):
                group = GroupProfile.objects.get(pk=request.POST['group'])
                if 'remUser' in request.POST:
                    member = User.objects.get(pk=request.POST['remUser'])
                    set_notification('group', data={'group': group, 'member': member})
                    group.member.remove(member)
                    context['success_msg'] = "Mitglied erfolgreich entfernt."
            else:
                gpe_form = GroupProfileEditForm(request.POST, request.FILES, instance=group)
                if 'group_public' in request.POST:
                    group.password = ''
                    group.save()
                # if picture has changed, delete old picture
                # do not, if old picture was default picture
                if 'picture' in request.FILES or 'picture-clear' in request.POST:
                    print("test")
                    gpe_form.oldPicture = group.picture
                    if gpe_form.oldPicture != 'picture/gdefault.gif':
                        gpe_form.oldPicture.delete()
                if gpe_form.is_valid():
                    gpe_form.save()
                    context['success_msg'] = 'Gruppendaten wurden erfolgreich aktualisiert.'
                else:
                    # return errors if GroupProfileEditForm is not valid
                    context['error_msg'] = gpe_form.errors
                context['gpeForm'] = gpe_form

        # return information to render settings.html
        return render(request, 'settings.html', context)
