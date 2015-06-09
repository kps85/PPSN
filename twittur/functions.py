import datetime

from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist

from .models import Message, Hashtag
from .forms import MessageForm


# messagebox clicked on pencil button
def msgDialog(request):
    curUser = User.objects.get(pk=request.user.id)

    if request.method == 'POST':
        msgForm = MessageForm(request.POST)
        if msgForm.is_valid():
            msgForm.save()
            msg_to_db(msgForm.instance)
            msgForm.save()
            # save this shit for the next step

    msgForm = MessageForm(initial={'user': curUser.id, 'date': datetime.datetime.now()})
    return msgForm


# edit or update Message
def editMessage(request):
    if 'delMessage' in request.POST:                                        # if Message should be deleted
        if Message.objects.filter(pk=request.POST['delMessage']).exists():  # if Message exists
            curMsg = Message.objects.get(pk=request.POST['delMessage'])     # select Message
            curMsg.delete()                                                 # delete selected Message
        return 'Nachricht gel&ouml;scht!'                                   # return info

    elif 'updateMsg' in request.POST:                                       # if Message should be updated
        if Message.objects.filter(pk=request.POST['updateMsg']).exists():   # if Message exists
            curMsg = Message.objects.get(pk=request.POST['updateMsg'])      # select Message
            curMsg.text = request.POST['updatedText']                       # set Message text
            msg_to_db(curMsg)                                               # ???
            curMsg.save()                                                   # save and update Message
        return 'Nachricht erfolgreich aktualisiert!'                        # return info

    else:                                                                   # if Message should be posted
        return 'Nachricht erfolgreich gesendet!'                            # return info, post routine in msgDialog()


# Message to database, save hashtags and attags in text into database
# (2) edit: changed message may contains other hashtags and attags or hashtags and attags may removed
def msg_to_db(message):
    hashtaglist = []
    attaglist = []

    # Step 1: replace all # and @ with link
    for word in message.text.split():
        # find all words starts with "#". No "/" allowed in hashtag.
        if word[0] == "#":
            if "/" in word:
                pass
            else:
                # database will save hashtag instead of #hashtag
                try:
                    hashtag = Hashtag.objects.get(name__exact=str(word[1:]))
                except ObjectDoesNotExist:
                    hashtag = Hashtag(name=str(word[1:]))
                    hashtag.save()

                message.hashtags.add(hashtag)
                hashtaglist.append(hashtag)
        # now find in text all words start with "@". Its important to find this user in database.
        if word[0] == "@":
            # database will save user instead of @user
            try:
                user = User.objects.get(username__exact=str(word[1:]))
            except ObjectDoesNotExist:
                pass
            else:
                message.attags.add(user)
                attaglist.append(user)

    # (2) check for hashtags and attags in database (remove if no reference), only for edit
    for dbhashtag in message.hashtags.all():
        if dbhashtag not in hashtaglist:
            message.hashtags.remove(dbhashtag)
    for dbattag in message.attags.all():
        if dbattag not in attaglist:
            message.attags.remove(dbattag)

    return message


# Database message to message (in template), replace all hashtags and attags in message with links
def dbm_to_m(message):
    # get hashtags and attags (models.ManyToMany) in message from database
    hashtag_list = message.hashtags.all()
    attag_list = message.attags.all()

    # message contains hashtags or atttags
    if attag_list or hashtag_list:
        for word in message.text.split():
            # find all words starts with "#" and replace them with a link. No "/" allowed in hashtag.
            if word[0] == "#" and (Hashtag.objects.get(name=word[1:]) in hashtag_list):
                href = '<a href="/twittur/hashtag/' + word[1:] + '">' + word + '</a>'
                message.text = message.text.replace(word, href)
            # now find in text all words start with "@". Its important to find this user in database.
            # if this user doesnt exist -> no need to set a link
            # else we will set a link to his profile
            if word[0] == "@" and (User.objects.get(username=word[1:]) in attag_list):
                    href = '<a href="/twittur/profile/' + word[1:] + '">' + word + '</a>'
                    message.text = message.text.replace(word, href)
    return message