import random

from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Count, Q
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render

from .forms import GroupProfileForm, GroupProfileEditForm
from .functions import getNotificationCount, msgDialog
from .models import GroupProfile, Hashtag, Nav, UserProfile


def group(request, groupshort):

    if not request.user.is_authenticated():
        return HttpResponseRedirect('/twittur/login/')

    show_member, is_member, button_text = False, False, None

    # Follow List
    curUser = UserProfile.objects.get(userprofile=request.user)
    follow_list = curUser.follow.all()
    # Group List
    group_sb_list = GroupProfile.objects.all().filter(Q(member__exact=request.user))
    # Beliebte Themen
    hot_list = Hashtag.objects.annotate(hashtag_count=Count('hashtags__hashtags__name')) \
                   .order_by('-hashtag_count')[:5]

    group = GroupProfile.objects.get(short__exact=groupshort)
    member_list = group.member.all()
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

    # TODO Message

    context = {
        'active_page': 'group',
        'curUser': request.user,
        'nav': Nav.nav,
        'msgForm': msgDialog(request),
        'hot_list': hot_list,
        'follow_sb_list': sorted(follow_list, key=lambda x: random.random())[:5],
        'group_sb_list': group_sb_list,
        'group': group,
        'member_list': member_list,
        'show_member': show_member,
        'is_member': is_member,
        'button_text': button_text,
    }
    return render(request, 'profile.html', context)

# view for add a new group
def addgroup(request):

    if not request.user.is_authenticated():
        return HttpResponseRedirect('/twittur/login/')

    # Follow List
    curUser = UserProfile.objects.get(userprofile=request.user)
    follow_list = curUser.follow.all()
    # Group List
    group_sb_list = GroupProfile.objects.all().filter(Q(member__exact=request.user))
    # Beliebte Themen
    hot_list = Hashtag.objects.annotate(hashtag_count=Count('hashtags__hashtags__name')) \
                   .order_by('-hashtag_count')[:5]

    error_msg = {}

    if request.POST:
        groupProfileForm = GroupProfileForm(request.POST)

        if groupProfileForm.is_valid():
            try:
                group = GroupProfile.objects.get(name__exact=groupProfileForm.instance.name)
            except ObjectDoesNotExist:
                if (request.POST.get('password') != request.POST.get('ack_password')):
                    error_msg['error_passwords_diff'] = "Passwoerter sind nicht gleich!"
                    context = {
                                'error_msg': error_msg,
                                'groupProfileForm': groupProfileForm,
                                'nav': Nav.nav,
                                }
                    return render(request, 'addgroup.html', context)

                groupProfileForm.instance.groupprofile = groupProfileForm.instance
                groupProfileForm.instance.admin = request.user
                groupProfileForm.save()
                groupProfileForm.instance.member.add(request.user)

                return HttpResponseRedirect('/twittur/group/' + groupProfileForm.instance.short)
            else:
                error_msg['error_grp_name_exist'] = "Gruppenname ist schon vergeben!"

    groupProfileForm = GroupProfileForm()
    context = {
        'active_page': 'group',
        'nav': Nav.nav,
        'error_msg': error_msg,
        'groupProfileForm': groupProfileForm,
        'msgForm': msgDialog(request),
        'hot_list': hot_list,
        'follow_sb_list': sorted(follow_list, key=lambda x: random.random())[:5],
        'group_sb_list': group_sb_list,
    }
    return render(request, 'addgroup.html', context)

def joingroup(request, groupname):
    return 0

# function for delete/join/leave group
def djlgroup(request, groupshort):

    print(request.POST)

    # Be sure this is the right function, true -> get group object
    if 'delete_join_group' in request.POST:
        group = GroupProfile.objects.get(short__exact=groupshort)
        # Admin function: delete group
        if group.admin == request.user:
            print("is admin")
            return HttpResponseRedirect('/twittur/group/'+groupshort+'/settings')

        # Member function:
        else:
            print('is member')
            # check if user is in group or not
            try:
                group.member.get(username__exact=request.user.username)
            # User does not exist, means he is not in group -> add him (password required?) -> redirect to groupsite
            except ObjectDoesNotExist:
                # TODO and discuss!!! case: if password is required here -> redirect to loginsite (not implement yet)
                if 'joinWithPassword' in request.POST:
                    if group.password == request.POST.get('password'):
                        group.member.add(request.user)
                    else:
                        return HttpResponse("Falsches Passwort!")
                else:
                    group.member.add(request.user)
            # User exists -> delete him from group
            else:
                group.member.remove(request.user)

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

    # Notification
    new = getNotificationCount(request.user)

    # check if group should be deleted
    # if true: delete group, return to index
    if request.method == 'POST' and request.POST['delete'] == 'true':
        group.delete()
        return HttpResponseRedirect('/twittur/')
    # else: validate userForm and userDataForm and save changes
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
            # return errors if userForm is not valid
            error_msg = gpeForm.errors

    # initialize GroupProfileEditForm with current groups information
    gpeForm = GroupProfileEditForm(instance=group)

    # return relevant information to render settings.html
    context = {
        'active_page': 'settings',
        'nav': Nav.nav,
        'new': new,
        'msgForm': msgDialog(request),
        'success_msg': success_msg,
        'error_msg': error_msg,
        'group': group,
        'gpeForm': gpeForm,
    }
    return render(request, 'settings.html', context)
