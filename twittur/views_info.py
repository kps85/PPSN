from django.http import HttpResponseRedirect
from django.shortcuts import render

from django.contrib.auth.models import User

from .models import Nav, FAQ
from .forms import FAQForm
from .views import msgDialog


# Page: 'Info'
# - shows: Impressum, Projekt-Team, Projekt (Aufgabenstellung, Ziel)
# - template: info.html
def info(request):
    # check if user is logged in
    # if user is not logged in, redirect to FTU
    if not request.user.is_authenticated():
        return HttpResponseRedirect('/twittur/login/')

    # select admin users as Projekt-Team
    projektTeam = User.objects.filter(is_superuser=True).order_by('last_name')

    # return relevant information to render info.html
    context = {
        'active_page': 'info',
        'nav': Nav.nav,
        'msgForm': msgDialog(request),
        'team': projektTeam
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
    success_msg, error_msg = None, None

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
    faqMain = FAQ.objects.filter(category='Allgemeine Frage')
    faqStart = FAQ.objects.filter(category='Startseite')
    faqProfile = FAQ.objects.filter(category='Profilseite')
    faqInfo = FAQ.objects.filter(category='Infoseite')
    faqSettings = FAQ.objects.filter(category='Einstellungen')

    # sum FAQs into one list
    FAQs = [faqMain, faqStart, faqProfile, faqInfo, faqSettings]

    # return relevant information to render info_faq.html
    context = {
        'active_page': 'info',
        'nav': Nav.nav,
        'msgForm': msgDialog(request),
        'faqForm': faqForm,
        'faqMain': faqMain,
        'faqStart': faqStart,
        'faqProfile': faqProfile,
        'faqInfo': faqInfo,
        'faqSettings': faqSettings,
        'FAQs': FAQs,
        'success_msg': success_msg,
        'error_msg': error_msg
    }
    return render(request, 'info_faq.html', context)


# Page: 'Support'
# - allows: submitting diverse requests TODO: implement data processing
# - template: info_support.html
def support(request):
    # check if user is logged in
    # if user is not logged in, redirect to FTU
    if not request.user.is_authenticated():
        return HttpResponseRedirect('/twittur/login/')

    # return relevant information to render info_faq.html
    context = {
        'active_page': 'info',
        'nav': Nav.nav,
        'msgForm': msgDialog(request)
    }
    return render(request, 'info_support.html', context)
