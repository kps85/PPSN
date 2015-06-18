from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.shortcuts import render

from .forms import GroupProfileForm
from .functions import msgDialog
from .models import Nav, GroupProfile, UserProfile


def group(request, groupshort):

    if not request.user.is_authenticated():
        return HttpResponseRedirect('/twittur/login/')

    is_member, button_text = False, None

    # Follows
    curUser = UserProfile.objects.get(userprofile=request.user)
    follow_list = curUser.follow.all()

    # Groups
    group_list = GroupProfile.objects.all().filter(Q(member__exact=request.user))

    group = GroupProfile.objects.get(short__exact=groupshort)
    member_list = group.member.all()
    if request.user in member_list:
        if group.admin == request.user:
            button_text = '<span class="glyphicon glyphicon-log-out"></span> ' + group.short.upper() + ' aufl&ouml;sen'
        else:
            button_text = '<span class="glyphicon glyphicon-log-out"></span> ' + group.short.upper() + ' verlassen'
    else:
        button_text = '<span class="glyphicon glyphicon-log-in"></span> ' + group.short.upper() + ' beitreten'

    # TODO Message

    context = {
        'active_page': 'profile',
        'curUser': request.user,
        'nav': Nav.nav,
        'msgForm': msgDialog(request),
        'follow_list': follow_list,
        'group_list': group_list,
        'group': group,
        'member_list': member_list,
        'is_member': is_member,
        'button_text': button_text
    }
    return render(request, 'profile.html', context)

# view for add a new group
def addgroup(request):

    if not request.user.is_authenticated():
        return HttpResponseRedirect('/twittur/login/')

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
        'nav': Nav.nav,
        'error_msg': error_msg,
        'groupProfileForm': groupProfileForm,
    }
    return render(request, 'addgroup.html', context)

def joingroup(request, groupname):
    return 0

# function for delete/join/leave group
def djlgroup(request, groupshort):

    # Be sure this is the right function, true -> get group object
    if 'delete_join_group' in request.POST:
        group = GroupProfile.objects.get(short=groupshort)

        # Admin function: delete group
        if group.admin == request.user:
            print("is admin")
            group.delete()
            return HttpResponseRedirect('/twittur/')

        # Member function:
        else:
            print('is member')
            # check if user is in group or not
            try:
                group.member.get(username__exact=request.user.username)
            # User does not exist, means he is not in group -> add him (password required?) -> redirect to groupsite
            except ObjectDoesNotExist:
                # TODO and discuss!!! case: if password is required here -> redirect to loginsite (not implement yet)
                group.member.add(request.user)
                return HttpResponseRedirect('/twittur/group/'+groupshort)
            # User exists -> delete him from group
            else:
                group.member.remove(request.user)

        return HttpResponseRedirect('/twittur/group/'+groupshort)

# TODO
# - Sichtbarkeit von Nachrichten? (Passwort required oder nicht)
