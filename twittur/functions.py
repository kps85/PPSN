import copy, datetime, string

from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone

from .views import *
from .models import Message, Hashtag, NotificationM
from .forms import MessageForm


# messagebox clicked on pencil button
def msgDialog(request):
    curUser = User.objects.get(pk=request.user.id)

    if request.method == 'POST' and request.POST.get('codename') == 'message':
        msgForm = MessageForm(request.POST)
        if msgForm.is_valid():
            msgForm.save()
            msg_to_db(msgForm.instance)
            msgForm.save()
            # save this shit for the next step

    if request.method == 'POST' and request.POST.get('codename') == 'comment':

        msgForm = MessageForm(request.POST)
        if msgForm.is_valid():
            msgForm.save()
            message = Message.objects.get(id=request.POST.get('cmtToId'))
            msgForm.instance.comment = message
            msg_to_db(msgForm.instance)
            msgForm.save()
            # save this shit for the next step


    msgForm = MessageForm(initial={'user': curUser.id, 'date': datetime.datetime.now()})
#    print(msgForm.instance.text)
    return msgForm


# edit or update Message
def editMessage(request):
    if 'delMessage' in request.POST:                                        # if Message should be deleted
        if Message.objects.filter(comment=request.POST['delMessage']).exists():
            msg = Message.objects.get(pk=request.POST['delMessage'])
            comments = Message.objects.filter(comment=msg)
            for obj in comments:
                obj.delete()
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

    elif 'updateCmt' in request.POST:                                       # if Message should be updated
        if Message.objects.filter(pk=request.POST['updateCmt']).exists():   # if Message exists
            curMsg = Message.objects.get(pk=request.POST['updateCmt'])      # select Message
            curMsg.text = request.POST['updatedText']                       # set Message text
            msg_to_db(curMsg)                                               # ???
            curMsg.save()                                                   # save and update Message
        return 'Kommentar erfolgreich aktualisiert!'                        # return info

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
                notification = NotificationM(user=user, message=message, read=False)
                notification.save()
                print(message.attags.all())
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


def getMessages(data):

    result, has_msg, list_end = {}, False, False
    dbmessage_list = getMessageList(data['page'], data['user'])
    curDate = timezone.make_aware(datetime.datetime.now() - datetime.timedelta(minutes=10),
                                  timezone.get_current_timezone())

    message_list, comment_list, comment_count = [], [], []
    for message in dbmessage_list:
        if message.date > curDate:
            message.editable = True
        c = getComments(message, curDate)
        comment_list.append(c)
        comment_count.append(getCommentCount(message))

        copy_message = copy.copy(message)
        message_list.append(dbm_to_m(copy_message))

    if len(message_list) > 0:
        has_msg = True

    print(data['end'])
    if 'end' in data:
        if data['end'] is None or data['end'] >= len(message_list):
            list_end = True

    result = {
        'message_list': message_list,
        'dbmessage_list': dbmessage_list,
        'comment_list': comment_list,
        'comment_count': comment_count,
        'has_msg': has_msg,
        'list_end': list_end,
    }
    return result


# return Full Message List
def getMessageList(page, user):
    if page == 'index':
        dbmessage_list = Message.objects.all().filter(
            ( Q(user__exact=user) | Q(user__exact=user[0].userprofile.follow.all())
            | Q(attags = None) | Q(attags = user) )
            & Q(comment = None)
        ).order_by('-date')
    elif page == 'profile':
        dbmessage_list = Message.objects.all().select_related('user__userprofile').filter(
            Q(user__exact=user) | Q(attags__username__exact=user.username)
        ).order_by('-date')
    elif page == 'hashtag':
        dbmessage_list = Message.objects.all().filter(
            hashtags__name=user
        ).order_by('-date')
    elif page == 'search':
        query = Q(user__username__in=user)
        for term in user:
            query |= Q(text__contains=term) | Q(user__username__contains=term)
        dbmessage_list = Message.objects.all().select_related('user__userprofile').filter(
            query
        ).order_by('-date')
    elif page == 'ftu':
        dbmessage_list = Message.objects.all()
    else:
        dbmessage_list = Message.objects.filter(pk=page)

    return dbmessage_list


# return Comment List for specific Message
def getComments(message, curDate):
    comments = Message.objects.filter(comment=message)
    c = []
    if comments:
        for co in comments:
            cc, ccc = [], getComments(co, curDate)
            if co.date > curDate:
                co.editable = True
            cc.append(dbm_to_m(co))
            if ccc:
                cc.append(ccc)
            c.append(cc)
    return c


def getCommentCount(message):
    count = 0
    comments = Message.objects.filter(comment=message)
    for comment in comments:
        count += getCommentCount(comment) + 1
    return count


def getNotificationCount(user):
    newM = NotificationM.objects.filter(Q(read=False) & Q(user=user)).count()
    newF = NotificationF.objects.filter(Q(read=False) & Q(you=user)).count()
    newC = Message.objects.all().filter(Q(read=False) & Q(comment__user=user)).exclude(user=user).count()
    new = newF + newM + newC

    return new


# generate Sidebar Widgets and return them
def getWidgets(request):
    userProfile = UserProfile.objects.get(userprofile=request.user)
    sidebar = {
        'msgForm': msgDialog(request),
        'userProfile': userProfile,
        'follow_list': userProfile.follow.all(), # Follow List
        'group_sb_list': GroupProfile.objects.all().filter(Q(member__exact=request.user)), # Group List
        'hot_list': Hashtag.objects.annotate(hashtag_count=Count('hashtags__hashtags__name')) \
                   .order_by('-hashtag_count')[:5], # Beliebte Themen
        'new': getNotificationCount(request.user), # Notifications
    }
    return sidebar


def pw_generator(size=6, chars=string.ascii_uppercase + string.digits): # found on http://goo.gl/RH995X
    return ''.join(random.choice(chars) for _ in range(size))