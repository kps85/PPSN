from django.core.mail import send_mail
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.utils.safestring import mark_safe

from django.contrib.auth.models import User

from .functions import getWidgets
from .models import Nav, FAQ
from .forms import FAQForm


# Page: 'Info'
# - shows: Impressum, Projekt-Team, Projekt (Aufgabenstellung, Ziel)
# - template: info.html
def info(request):
    # select admin users as Projekt-Team
    projektTeam = User.objects.filter(is_superuser=True).exclude(pk=15).order_by('last_name')

    # check if user is logged in
    # if user is not logged in, redirect to FTU
    if not request.user.is_authenticated():
        return render(request, 'info_guest.html', {'active_page': 'info_guest', 'team': projektTeam})
    else:
        # initialize sidebar lists
        widgets = getWidgets(request)

    # return relevant information to render info.html
    context = {
        'active_page': 'info', 'nav': Nav.nav, 'new': widgets['new'], 'msgForm': widgets['msgForm'],
        'team': projektTeam,
        'safetyLevels': widgets['safetyLevels']
    }
    return render(request, 'info.html', context)


# Page: 'FAQ'
# - shows: frequently asked questions
# - allows: adding and deleting FAQ entries
# - template: info_faq.html
def faq(request):
    # check if user is logged in
    # if user is not logged in, redirect to FTU
    if not request.user.is_authenticated():
        return HttpResponseRedirect('/twittur/login/')

    # initialize return information
    success_msg, error_msg, FAQs = None, None, []

    # initialize sidebar lists
    widgets = getWidgets(request)

    # adding a FAQ entry
    # form: FAQform from forms.py
    if request.method == 'POST':
        faqForm = FAQForm(request.POST)
        if faqForm.is_valid():
            faqForm.save()
            success_msg = "Neuer FAQ Eintrag hinzugef&uuml;gt!"

    # initialize FAQForm with current user as respondent
    faqForm = FAQForm(instance=request.user)

    # initialize FAQ list for each category
    faqCats = FAQ.objects.all().values('category').distinct().order_by('category')
    for cat in faqCats:
        faqList = FAQ.objects.filter(category=cat['category']).order_by('question')
        FAQs.append(faqList)

    # return relevant information to render info_faq.html
    context = {
        'active_page': 'info', 'nav': Nav.nav, 'new': widgets['new'], 'msgForm': widgets['msgForm'],
        'success_msg': success_msg, 'error_msg': error_msg, 'faqForm': faqForm,
        'FAQs': FAQs,
        'safetyLevels': widgets['safetyLevels']
    }
    return render(request, 'info_faq.html', context)


# Page: 'Support'
# - allows: submitting diverse requests
# - template: info_support.html
def support(request):
    # check if user is logged in
    # if user is not logged in, redirect to FTU
    if not request.user.is_authenticated():
        return HttpResponseRedirect('/twittur/login/')

    # initialize sidebar lists
    widgets = getWidgets(request)

    success_msg, hash = None, None
    team_list = User.objects.filter(is_superuser=True).order_by('last_name')
    cat_list = FAQ.objects.all().values('category').distinct()

    if request.method == 'POST':
        sender, recipient, subject, hash = request.user, [], request.POST['subject'], request.POST['hash']
        if 'staff' in request.POST:
            recipient.append(request.POST['staff'])
            message = sender.first_name + " " + sender.last_name + " (@" + sender.username + ") hat eine " \
                    + "Supportanfrage gestellt: \n" \
                    + "\n" \
                    + request.POST['message'] + "\n" \
                    + "\n" \
                    + "--------------------------------------------------\n" \
                    + "\n" \
                    + "von " + sender.first_name + " " + sender.last_name + " (@" + sender.username \
                    + ") auf twittur\n" \
                    + "Antworten an " + sender.email
        else:
            for member in team_list:
                recipient.append(member.email)
            topic = request.POST['topic']
            message = sender.first_name + " " + sender.last_name + " (@" + sender.username + ") hat eine " \
                    + "Frage zum Thema: " + topic + "\n" \
                    + "\n" \
                    + request.POST['message'] + "\n" \
                    + "\n" \
                    + "--------------------------------------------------\n" \
                    + "\n" \
                    + "Von " + sender.first_name + " " + sender.last_name + " (@" + sender.username \
                    + ") auf twittur.\n" \
                    + "Antworten an " + sender.email
        send_mail(subject, mark_safe(message), sender.email, recipient)
        success_msg = "Ihre Nachricht wurde erfolgreich abgeschickt!"

    # return relevant information to render info_faq.html
    context = {
        'active_page': 'info', 'nav': Nav.nav, 'new': widgets['new'], 'msgForm': widgets['msgForm'],
        'success_msg': success_msg, 'hash': hash, 'curUser': request.user,
        'team_list': team_list, 'cat_list': cat_list,
        'safetyLevels': widgets['safetyLevels']
    }
    return render(request, 'info_support.html', context)
