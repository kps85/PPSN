from django.core.mail import send_mail
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.utils.safestring import mark_safe

from django.contrib.auth.models import User

from .forms import FAQForm
from .functions import getContext
from .models import Nav, FAQ


# Page: 'Info'
# - shows: Impressum, Projekt-Team, Projekt (Aufgabenstellung, Ziel)
# - template: info.html
def InfoView(request):
    # select admin users as Projekt-Team
    projektTeam = User.objects.filter(is_superuser=True).exclude(pk=15).order_by('last_name')

    # check if user is logged in
    # if user is not logged in, redirect to FTU
    if not request.user.is_authenticated():
        return render(request, 'info_guest.html', {'active_page': 'info_guest', 'team': projektTeam})

    # return relevant information to render info.html
    context = getContext(request, 'info', request.user)
    context['team'] = projektTeam
    context['FAQs'] = getFAQs()
    return render(request, 'info.html', context)


# Page: 'FAQ'
# - shows: frequently asked questions
# - allows: adding and deleting FAQ entries
# - template: info_faq.html
def FAQView(request):
    # check if user is logged in
    # if user is not logged in, redirect to FTU
    if not request.user.is_authenticated():
        return HttpResponseRedirect('/twittur/login/')

    context = getContext(request, 'info', request.user)

    # adding a FAQ entry
    # form: FAQform from forms.py
    if request.method == 'POST':
        faqForm = FAQForm(request.POST)
        if faqForm.is_valid():
            faqForm.save()
            context['success_msg'] = "Neuer FAQ Eintrag hinzugef&uuml;gt!"

    # initialize FAQForm with current user as respondent
    context['faqForm'] = FAQForm(instance=request.user)
    context['FAQs'] = getFAQs()

    # return relevant information to render info_faq.html
    return render(request, 'info_faq.html', context)


# Page: 'Support'
# - allows: submitting diverse requests
# - template: info_support.html
def SupportView(request):
    # check if user is logged in
    # if user is not logged in, redirect to FTU
    if not request.user.is_authenticated():
        return HttpResponseRedirect('/twittur/login/')

    context = getContext(request, 'info', request.user)
    context['team_list'] = User.objects.filter(is_superuser=True).order_by('last_name')
    context['cat_list'] = FAQ.objects.all().values('category').distinct()

    if request.method == 'POST':
        sender, recipient, subject = request.user, [], request.POST['subject']
        context['hash'] = request.POST['hash']
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
            for member in context['team_list']:
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
        context['success_msg'] = "Ihre Nachricht wurde erfolgreich abgeschickt!"

    context['FAQs'] = getFAQs()
    # return relevant information to render info_faq.html
    return render(request, 'info_support.html', context)


def getFAQs():
    # initialize FAQ list for each category
    FAQs, faqCats = [], FAQ.objects.all().values('category').distinct().order_by('category')
    for cat in faqCats:
        faqList = FAQ.objects.filter(category=cat['category']).order_by('question')
        FAQs.append(faqList)
    return FAQs
