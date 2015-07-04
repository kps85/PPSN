"""
-*- coding: utf-8 -*-
@package twittur
@author twittur-Team (Lilia B., Ming C., William C., Karl S., Thomas T., Steffen Z.)
Info Views
- InfoView:            landing page for logged-in users
- FAQView:            landing page for guests
- SupportView:          profile page for logged-in users
"""

from django.core.mail import send_mail
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.utils.safestring import mark_safe

from django.contrib.auth.models import User

from .forms import FAQForm
from .functions import get_context, get_faqs
from .models import FAQ


# Page: "Info"
def info_view(request):
    """
    view to display project team and project information
    :param request:
    :return: rendered HTML in template 'info.html'
    """

    # select admin users as projectTeam
    project_team = User.objects.filter(is_superuser=True).exclude(pk=15).order_by('last_name')

    if not request.user.is_authenticated():                             # check if user is logged in
        return render(request, 'info_guest.html',                       # if not -> redirect to info page for guests
                      {'active_page': 'info_guest', 'team': project_team})

    # initialize data dictionary 'context' with relevant display information
    context = get_context(request, 'info', request.user)
    context['team'], context['FAQs'] = project_team, get_faqs()

    return render(request, 'info.html', context)


# Page: "FAQ"
def faq_view(request):
    """
    view to display frequently asked questions
    superuser can add entries
    :param request:
    :return: rendered HTML in template 'info_faq.html'
    """

    if not request.user.is_authenticated():             # check if user is logged in
        return HttpResponseRedirect('/twittur/login/')  # if not -> redirect to FTU

    # initialize data dictionary 'context' with relevant display information
    context = get_context(request, 'info', request.user)

    # adding a FAQ entry
    # form: FAQform from forms.py
    if request.method == 'POST':
        faq_form = FAQForm(request.POST)
        if faq_form.is_valid():
            faq_form.save()
            context['success_msg'] = "Neuer FAQ Eintrag hinzugef&uuml;gt!"

    # initialize FAQForm with current user as respondent
    context['faqForm'], context['FAQs'] = FAQForm(instance=request.user), get_faqs()

    return render(request, 'info_faq.html', context)


# Page: "Support"
def support_view(request):
    """
    view to display support forms which send emails to single superusers or the whole team
    :param request:
    :return: rendered HTML in template 'info_support.html'
    """

    if not request.user.is_authenticated():             # check if user is logged in
        return HttpResponseRedirect('/twittur/login/')  # if not -> redirect to FTU

    # initialize data dictionary 'context' with relevant display information
    context = get_context(request, 'info', request.user)
    context['team_list'] = User.objects.filter(is_superuser=True).exclude(pk=15).order_by('last_name')
    context['cat_list'] = FAQ.objects.all().values('category').distinct()
    context['FAQs'] = get_faqs()

    if request.method == 'POST':
        sender, recipient, subject = request.user, [], request.POST['subject']
        context['hash'] = request.POST['hash']
        if 'staff' in request.POST:
            recipient.append(request.POST['staff'])
            message = sender.first_name + " " + sender.last_name + " (@" + sender.username + ") "
            message += "hat eine Supportanfrage gestellt: \n\n"
            message += request.POST['message'] + "\n\n"
            message += "--------------------------------------------------\n\n"
            message += "Von " + sender.first_name + " " + sender.last_name + " (@" + sender.username + ") auf twittur\n"
            message += "Antworten an " + sender.email
        else:
            for member in context['team_list']:
                recipient.append(member.email)
            topic = request.POST['topic']
            message = sender.first_name + " " + sender.last_name + " (@" + sender.username + ") hat eine "
            message += "Frage zum Thema: " + topic + "\n\n"
            message += request.POST['message'] + "\n\n"
            message += "--------------------------------------------------\n\n"
            message += "Von " + sender.first_name + " " + sender.last_name + " (@" + sender.username + ") auf twittur\n"
            message += "Antworten an " + sender.email
        send_mail(subject, mark_safe(message), sender.email, recipient)
        context['success_msg'] = "Ihre Nachricht wurde erfolgreich abgeschickt!"

    return render(request, 'info_support.html', context)
