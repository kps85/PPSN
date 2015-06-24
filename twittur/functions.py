import copy, datetime, string

from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Count
from django.utils import timezone

from .views import *
from .models import GroupProfile, Message, Hashtag, Notification
from .forms import MessageForm
import re


# messagebox clicked on pencil button
def msgDialog(request):
    if request.method == 'POST':
        if request.POST.get('codename') == 'message':
            msgForm = MessageForm(request.POST, request.FILES)
            if msgForm.is_valid():
                msgForm.save()
                msg_to_db(msgForm.instance)
                msgForm.save()
                # save this shit for the next step

        elif request.POST.get('codename') == 'comment':
            msgForm = MessageForm(request.POST)
            if msgForm.is_valid():
                msgForm.save()
                message = Message.objects.get(id=request.POST.get('cmtToId'))
                msgForm.instance.comment = message
                msg_to_db(msgForm.instance)
                msgForm.save()
                if message.user != request.user:
                    note = request.user.username + ' hat auf deine Nachricht geantwortet.'
                    setNotification('comment', data={'user': message.user, 'message': msgForm.instance, 'note': note})
                # save this shit for the next step

    msgForm = MessageForm(initial={'user': request.user.id, 'date': datetime.datetime.now()})
    return msgForm


# edit or update Message
def editMessage(request):
    if 'updateMsg' in request.POST:                                       # if Message should be updated
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

    elif 'remUser' in request.POST:
        group = GroupProfile.objects.get(pk=request.POST['group'])
        member = User.objects.get(pk=request.POST['remUser'])
        setNotification('group', data={'group': group, 'member': member})
        group.member.remove(member)
        return "Mitglied erfolgreich entfernt."

    elif 'promUser' in request.POST:
        group = GroupProfile.objects.get(pk=request.POST['group'])
        member = User.objects.get(pk=request.POST['promUser'])
        setNotification('group_admin', data={'group': group, 'member': member})
        group.admin = member
        group.save()
        return "Mitglied erfolgreich bef&ouml;rdert."

    else:                                                                   # if Message should be posted
        return 'Nachricht erfolgreich gesendet!'                            # return info, post routine in msgDialog()


# Message to database, save hashtags and attags in text into database
# (2) edit: changed message may contains other hashtags and attags or hashtags and attags may removed
def msg_to_db(message):
    hashtaglist, attaglist = [], []

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
                if message.user != user:
                    setNotification('message', data={'user': user, 'message': message})
                attaglist.append(user)

        if word[0] == "&":
            # database will save group instead of @group
            try:
                group = GroupProfile.objects.get(short__exact=str(word[1:]))

            except ObjectDoesNotExist:
                if message.group != None:
                    message.group = None
                pass
            else:
                message.group = group

    # (2) check for hashtags and attags in database (remove if no reference), only for edit
    for dbhashtag in message.hashtags.all():
        if dbhashtag not in hashtaglist:
            message.hashtags.remove(dbhashtag)
    for dbattag in message.attags.all():
        if dbattag not in attaglist:
            attag = Notification.objects.get(
                Q(user=dbattag) & Q(message=message)
            )
            attag.delete()
    return message


# Database message to message (in template), replace all hashtags and attags in message with links
def dbm_to_m(message):
    # get hashtags and attags (models.ManyToMany) in message from database
    hashtag_list = message.hashtags.all()
    attag_list = message.attags.all()
    group = message.group
    urls = re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', message.text)
    # message contains hashtags or atttags
    if attag_list or hashtag_list or group:
        for word in message.text.split():
            href = ""
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

            if word[0] == '&' and group.short == word[1:]:
                href = '<a href="/twittur/group/' + word[1:] + '">' + word +'</a>'
                message.text = message.text.replace(word, href)

    if urls:
        for url in urls:
            href = '<a href="' + url + '">' + url + '</a>'
            message.text = message.text.replace(url, href)
    return message


def getMessages(data):
    result = {
        'has_msg': False
    }

    if 'end' not in data:
        result['list_end'] = 5
    else:
        if data['end'] is None:
            result['list_end'] = 5
        elif data['end'] == 'True':
            result['list_end'] = None
        else:
            result['list_end'] = int(data['end'])

    if 'end' in data['request'].POST:
        result['list_end'] = int(data['request'].POST.get('end'))

    dbmessage_list = getMessageList(data['page'], data['data'])
    curDate = timezone.make_aware(datetime.datetime.now() - datetime.timedelta(minutes=10),
                                  timezone.get_current_timezone())

    userprofile = UserProfile.objects.get(userprofile=data['request'].user)
    ignoreM_list = userprofile.ignoreM.all()
    ignoreU_list = userprofile.ignoreU.all()

    message_list, comment_list, comment_count = [], [], []
    for message in dbmessage_list:
        if message.date > curDate:
            message.editable = True
        c = getComments(data={
            'message': message, 'curDate': curDate, 'ignMsgList': ignoreM_list, 'ignUsrList': ignoreU_list
        })
        comment_list.append(c)
        comment_count.append(getCommentCount(message))

        # if User ignored this message -> boolean ignore = True, this change will not effect db (no save())
        if message in ignoreM_list:
            message.ignore = True
            message_list.append(message)
        elif message.user in ignoreU_list:
            message.ignore = True
            message_list.append(message)
        else:
            copy_message = copy.copy(message)
            message_list.append(dbm_to_m(copy_message))

    if len(message_list) > 0:
        result['has_msg'] = True

    result['list_length'] = len(message_list)
    result['message_list'] = zip(
        message_list[:result['list_end']], dbmessage_list[:result['list_end']], comment_list, comment_count
    )

    if result['list_end'] is None or result['list_end'] >= len(message_list):
        result['list_end'] = True

    return result


# return Full Message List
def getMessageList(page, data):
    if page == 'index':
        dbmessage_list = Message.objects.all().filter(
            ( Q(user__exact=data) | Q(user__exact=data[0].userprofile.follow.all())
            | Q(attags = None) | Q(attags = data) )
            & Q(comment = None)
        ).order_by('-date')
    elif page == 'group':
        dbmessage_list = Message.objects.all().filter(
            Q(group=data) & Q(comment=None)
        ).order_by('-date')
    elif page == 'profile':
        dbmessage_list = Message.objects.all().select_related('user__userprofile').filter(
            Q(user__exact=data) | Q(attags__username__exact=data.username)
        ).order_by('-date')
    elif page == 'hashtag':
        dbmessage_list = Message.objects.all().filter(
            hashtags__name=data
        ).order_by('-date')
    elif page == 'search':
        query = Q(user__username__in=data)
        for term in data:
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
def getComments(data):
    comments = Message.objects.filter(comment=data['message'])
    c = []
    if comments:
        for co in comments:
            cc, ccc = [], getComments(data={
                'message': co, 'curDate': data['curDate'],
                'ignMsgList': data['ignMsgList'], 'ignUsrList': data['ignUsrList']
            })
            if co.date > data['curDate']:
                co.editable = True
            if co in data['ignMsgList'] or co.user in data['ignUsrList']:
                co.ignore = True
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


def setNotification(type, data):
    ntfc = None
    if type == 'follower':
        ntfc = Notification(user=data['user'], follower=data['follower'], note=data['note'])
    elif type == 'message':
        ntfc = Notification(
            user=data['user'], message=data['message'],
            note='Du wurdest in einer Nachricht erw&auml;hnt.'
        )
    elif type == 'comment':
        ntfc = Notification(user=data['user'], message=data['message'], comment=True, note=data['note'])
    elif type == 'group':
        if 'note' not in data:
            data['note'] = 'Du wurdest aus der Gruppe entfernt.'
        ntfc = Notification(user=data['member'], group=data['group'], note=data['note'])
    elif type == 'group_admin':
        if 'note' not in data:
            data['note'] = 'Du wurdest in der Gruppe ' + data['group'].short + ' zum Admin bef&ouml;rdert.'
        ntfc = Notification(user=data['member'], group=data['group'], note=data['note'])

    ntfc.save()
    return ntfc


def getNotificationCount(user):
    return Notification.objects.filter(
        Q(read=False) & Q(user=user)
    ).count()


# generate Widgets and return them
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