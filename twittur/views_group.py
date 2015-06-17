__author__ = 'willycai'


from django.shortcuts import render
from django.http import HttpResponseRedirect
from .models import Nav, GroupProfile
from django.core.exceptions import ObjectDoesNotExist
from .forms import GroupProfileForm

# this is the basic view for group (para: groupname)
def group(request, groupname):

    if not request.user.is_authenticated():
        return HttpResponseRedirect('/twittur/login/')

    group = GroupProfile.objects.get(name__exact=groupname)
    member_list = group.member.all()
    curUser = request.user
    context = {
        'group': group,
        'member_list': member_list,
        'curUser': curUser,
        'nav': Nav.nav,
    }
    return render(request, 'group.html', context)

# view for add a new group
def addgroup(request):

    if not request.user.is_authenticated():
        return HttpResponseRedirect('/twittur/login/')

    error = None

    if request.POST:
        groupProfileForm = GroupProfileForm(request.POST)
        print(groupProfileForm.is_valid())
        if groupProfileForm.is_valid():
            try:
                group = GroupProfile.objects.get(name__exact=groupProfileForm.instance.name)
            except ObjectDoesNotExist:
                if (request.POST.get('password') != request.POST.get('ack_password')):
                    error = "Passwoerter sind nicht gleich!"
                    context = {
                                'error': error,
                                'groupProfileForm': groupProfileForm,
                                'nav': Nav.nav,
                                }
                    return render(request, 'addgroup.html', context)

                groupProfileForm.instance.groupprofile = groupProfileForm.instance
                groupProfileForm.instance.admin = request.user
                groupProfileForm.save()
                groupProfileForm.instance.member.add(request.user)

                return HttpResponseRedirect('/twittur/group/' + groupProfileForm.instance.name)
            else:
                error = "Gruppenname ist schon vergeben, bitch!"

    groupProfileForm = GroupProfileForm()
    context = {
        'error': error,
        'groupProfileForm': groupProfileForm,
        'nav': Nav.nav,

    }

    return render(request, 'addgroup.html', context)

def logingroup(request, groupname):
    return 0