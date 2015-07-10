# -*- coding: utf-8 -*-
"""
@package twittur
@author twittur-Team (Lilia B., Ming C., William C., Karl S., Thomas T., Steffen Z.)
Method Collection
- logout                ends the users session
- getContext            returns context dictionary with relevant display information
- msgDialog             returns message form for new message or comment
- msg_to_db             prepares the message to be stored in db
- checkhashtag          checks for existing hashtags in a message
- dbm_to_m              gets a message from database with attags, hashtags and groups linked
- getMessages           returns a dictionary of message lists
- getMessageList        returns a list of messages
- getComments           returns comments of specific message
- getCommentCount       returns count of comments for specific message
- load_more             loads further messages for different views
- update                updates a message with current information
- setNotification       returns users notifications
- getDisciplines        returns a list of academic disciplines
- getSafetyLevels       returns a list of safety levels for current user
- elimDups              eliminates duplicates in a message list
- pw_generator          generates a random password
"""

import copy
import datetime
import operator
import random
import re
import string
import hashlib

from django.conf import settings
from django.contrib import auth
from django.core.mail import send_mail
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.utils import timezone

from .models import FAQ, GroupProfile, Hashtag, Message, Nav, Notification, User, UserProfile
from .forms import MessageForm


def logout(request):
    """
    method to end logged-in users session
    :param request:
    :return: redirect to index (landing-page)
    """

    auth.logout(request)
    return HttpResponseRedirect(reverse("twittur:index"))


# initialize global data dictionary
def get_context(request, page=None, user=None):
    """

    :param request:
    :param page:
    :param user:
    :return:
    """

    user_profile = UserProfile.objects.get(userprofile=request.user)
    follow_list = user_profile.follow.all()
    # group_super_list is to hide default groups from sidebar // DISABLED for the moment
    # group_super_list = GroupProfile.objects.filter(pk__in=[24, 25, 34, 35, 36, 37, 38, 39])
    group_list = GroupProfile.objects.filter(
        Q(member__exact=request.user)
        # uncomment this and group_super_list to hide default groups from sidebar
        # & ~Q(pk__in=group_super_list) & ~Q(supergroup__in=group_super_list)
    )

    # collect hashtags, count them and order them by count reversed
    hashtag_count, hot_list = {}, []
    hashtag_list = Message.objects.all().exclude(hashtags=None).values("hashtags")
    for ht in hashtag_list:
        if ht['hashtags'] not in hashtag_count:
            hashtag_count[ht['hashtags']] = 1
        else:
            hashtag_count[ht['hashtags']] += 1
    hashtag_count_list = sorted(hashtag_count.items(), key=operator.itemgetter(1), reverse=True)
    for htc in hashtag_count_list[:5]:
        ht = Hashtag.objects.get(pk=htc[0])
        hot_list.append(ht)

    # set fav list, order by date of last message
    follow_sb_list = []
    messages = Message.objects.filter(user__in=follow_list).order_by('-date').values('user')
    for item in messages:
        usr = User.objects.get(pk=item['user'])
        if usr not in follow_sb_list:
            follow_sb_list.append(usr)

    # set group list, order by date of last message
    group_sb_list = []
    messages = Message.objects.filter(group__in=group_list).order_by('-date').values('group')
    for item in messages:
        grp = GroupProfile.objects.get(pk=item['group'])
        if grp not in group_sb_list:
            group_sb_list.append(grp)
        
    # generate URL for API
    location = reverse("twittur:get_notification")
    api_url = request.build_absolute_uri(location)

    # intialize data dictionary with relevant display information
    context = {
        'active_page': page,
        'nav': Nav.nav,
        'error_msg': {},
        'success_msg': None,
        'new': Notification.objects.filter(Q(read=False) & Q(user=request.user)).count(),
        'msgForm': msg_dialog(request),
        'apiUrl': api_url,
        'user': user,
        'userProfile': user_profile,
        'verifyHash': user_profile.verifyHash,
        'follow_list': follow_list,
        'follow_sb_list': follow_sb_list[:5],
        'group_list': group_list,
        'group_sb_list': group_sb_list[:5],
        'hot_list': hot_list[:5],

        'list_end': 5,
        'safetyLevels': get_safety_levels(request.user, True)
    }

    return context


# messagebox clicked on pencil button
def msg_dialog(request):
    """

    :param request:
    :return:
    """

    if request.method == 'POST' and 'codename' in request.POST:
        if request.POST['codename'] == 'message':
            msg_form = MessageForm(request.POST, request.FILES, user_id=request.user.id)
            if msg_form.is_valid():
                if 'safety' in request.POST:
                    if request.POST['safety'][:1] == '&':
                        group = GroupProfile.objects.get(short__exact=request.POST['safety'][1:])
                    elif request.POST['safety'] == 'Public':
                        group = None
                    else:
                        group = GroupProfile.objects.get(name__exact=request.POST['safety'])
                    msg_form.instance.group = group
                msg_form.save()
                msg_to_db(msg_form.instance)
                msg_form.save()                 # save this shit for the next step

        elif request.POST['codename'] == 'comment':
            msg_form = MessageForm(request.POST, user_id=request.user.id)
            if msg_form.is_valid():
                msg_form.save()
                message = Message.objects.get(id=request.POST['cmtToId'])
                msg_form.instance.comment = message
                msg_to_db(msg_form.instance)
                msg_form.save()                 # save this shit for the next step
                if message.user != request.user:
                    note = request.user.username + ' hat auf Ihre Nachricht geantwortet.'
                    set_notification('comment', data={
                        'user': message.user, 'message': msg_form.instance, 'note': note
                    })

    msg_form = MessageForm(initial={'user': request.user.id, 'date': datetime.datetime.now()},
                           user_id=request.user.id)
    return msg_form


# Message to database, save hashtags and attags in text into database
# (2) edit: changed message may contains other hashtags and attags or hashtags and attags may removed
def msg_to_db(message):
    """

    :param message:
    :return:
    """

    hashtaglist, attaglist = [], []
    regex_passed = False
    # Step 1: replace all # and @ with link
    for word in message.text.split():

        # find all words starts with "#".
        if word[0] == "#":
            check = re.findall(r'[a-zA-Z0-9-_äöüÄÖÜß()+-/=!?*]+', word[1:].encode('utf-8'))
            for item in check:
                item = item.decode('utf-8')
                if word[1:] == item:
                    regex_passed = True
            if regex_passed:
                if Hashtag.objects.filter(name__exact=word[1:].encode('utf-8')).exists():
                    hashtag = Hashtag.objects.get(name__exact=word[1:].encode('utf-8'))
                else:
                    hashtag = Hashtag(name=word[1:].encode('utf-8'))
                    hashtag.save()

                message.hashtags.add(hashtag)
                hashtaglist.append(hashtag)
        # now find in text all words start with "@". Its important to find this user in database.
        if word[0] == "@":
            # database will save user instead of @user
            if User.objects.filter(username__exact=word[1:]).exists():
                user = User.objects.get(username__exact=word[1:])
                if message.user != user:
                    set_notification('message', data={'user': user, 'message': message})
                attaglist.append(user)

        if word[0] == "&":
            # database will save group instead of @group
            if GroupProfile.objects.filter(short__exact=str(word[1:])).exists():
                group = GroupProfile.objects.get(short__exact=str(word[1:]))
                message.group = group
            else:
                if message.group is not None:
                    message.group = None

    # (2) check for hashtags and attags in database (remove if no reference), only for edit
    checkhashtag(message, hashtaglist)

    for dbattag in message.attags.all():
        if dbattag not in attaglist:
            attag = Notification.objects.get(Q(user=dbattag) & Q(message=message))
            attag.delete()

    return message


def checkhashtag(message, hashtaglist):
    """

    :param message:
    :param hashtaglist:
    :return:
    """

    for dbhashtag in message.hashtags.all():
        if dbhashtag not in hashtaglist:
            message.hashtags.remove(dbhashtag)
            # is there any message with this hashtag?
            hashtag_list = Message.objects.filter(hashtags=dbhashtag)
            if not hashtag_list:
                h = Hashtag.objects.get(name=dbhashtag)
                h.delete()


# Database message to message (in template), replace all hashtags and attags in message with links
def dbm_to_m(message):
    """

    :param message:
    :return:
    """

    # get hashtags and attags (models.ManyToMany) in message from database
    hashtag_list = message.hashtags.all()
    attag_list = message.attags.all()
    group = message.group
    urls = re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_#@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', message.text)

    # message contains hashtags or atttags
    if attag_list or hashtag_list or group:
        for word in message.text.split():
            # find all words starts with "#" and replace them with a link. No "/" allowed in hashtag.
            if word[0] == "#" and (word not in urls):
                if Hashtag.objects.filter(name=word[1:]).exists():
                    href = r'<a href="%s">%s</a>' % (reverse("twittur:hashtag", kwargs={'text': word[1:]}), word)
                    message.text = re.sub(r'(^|\s)%s($|\s)' % re.escape(word), r'\1%s\2' % href, message.text)

            # now find in text all words start with "@". Its important to find this user in database.
            # if this user doesnt exist -> no need to set a link
            # else we will set a link to his profile
            if word[0] == "@" and word not in urls:
                if User.objects.filter(Q(username=word[1:]) & Q(is_active=True)).exists()\
                        and User.objects.get(username=word[1:]) in attag_list:
                    href = '<a href="' + reverse("twittur:profile", kwargs={'user': word[1:]}) + '">' + word + '</a>'
                    message.text = message.text.replace(word, href)
            if word[0] == '&' and group.short == word[1:] and word not in urls:
                href = '<a href="' + reverse("twittur:group", kwargs={'groupshort': word[1:]}) + '">' + word + '</a>'
                message.text = message.text.replace(word, href)
    if urls:
        for url in urls:
            href = '<a href="' + url + '">' + url + '</a>'
            message.text = message.text.replace(url, href)

    return message


def get_messages(data):
    """
    creates a bundle of information to display messages
    :param data: a dictionary of page specific information
    :return: a dictionary with information to display messages
    """

    result = {'has_msg': False}

    # how many items should be displayed at first?
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

    # get a page specific list of messages
    db_message_list = get_message_list(data)
    cur_date = timezone.make_aware(datetime.datetime.now() - datetime.timedelta(minutes=10),
                                   timezone.get_current_timezone())

    # set the first item, where to start
    if 'post' in data['request'].GET:
        last_post_id = int(data['request'].GET.get('post'))
        result['list_start'] = 0
        for msg in db_message_list:
            result['list_start'] += 1
            if msg.id == last_post_id:
                break
    else:
        result['list_start'] = None

    user_profile = UserProfile.objects.get(userprofile=data['request'].user)
    ignore_m_list, ignore_u_list = user_profile.ignoreM.all(), user_profile.ignoreU.all()

    # create a bundle of data for the message_list (messages, forms, comments, counts)
    message_list, message_forms, comment_list, comment_count = [], [], [], []
    for message in db_message_list[result['list_start']:result['list_end']]:
        if message.date > cur_date:
            message.editable = True
        c = get_comments(data={
            'message': message, 'curDate': cur_date, 'ignMsgList': ignore_m_list, 'ignUsrList': ignore_u_list
        })
        comment_list.append(c)
        comment_count.append(get_comment_count(message))

        # if User ignored this message -> boolean ignore = True, this change will not effect db (no save())
        if message in ignore_m_list or message.user in ignore_u_list:
            message.ignore = True
            message_list.append(message)
        else:
            copy_message = copy.copy(message)
            message_list.append(dbm_to_m(copy_message))

        message_forms.append(MessageForm(instance=message))

    # check if messages exist, set boolean for frontend
    if len(db_message_list) > 0:
        result['has_msg'] = True

    # set list length and zip lists
    result['list_length'] = len(db_message_list)
    result['message_list'] = zip(
        message_list,
        db_message_list[result['list_start']:result['list_end']],
        message_forms, comment_list, comment_count
    )

    # check if last items where loaded
    if result['list_end'] is None or result['list_end'] >= len(db_message_list):
        result['list_end'] = True

    if 'length' in data['request'].GET:
        length = int(data['request'].GET.get('length'))
        if result['list_start'] > length:
            result['new_msgs'] = result['list_start'] - length

    return result


# return Full Message List
def get_message_list(data):
    """
    get all of the messages for a specific page
    :param data: page specific data
    :return: unformatted message list
    """

    page, data, request = data['page'], data['data'], data['request']
    usr_grps = GroupProfile.objects.filter(member=request.user)

    if page == 'index':
        db_message_list = Message.objects.filter(
            ((Q(user__exact=data)
              | (Q(user__exact=data.userprofile.follow.all()) & (Q(group__in=usr_grps) | Q(group=None)))
              | Q(attags=data))) & Q(comment=None)
        ).order_by('-date')
    elif page == 'group':
        grp = GroupProfile.objects.get(name=data)
        db_message_list = Message.objects.filter(
            Q(group=grp.id) & Q(comment=None)
        ).order_by('-date')
    elif page == 'profile':
        db_message_list = Message.objects.filter(
            (Q(user__exact=data) & (Q(group__in=usr_grps) | Q(group=None)))
            | Q(attags__username__exact=data.username)
        ).order_by('-date')
    elif page == 'hashtag':
        db_message_list = Message.objects.filter(
            Q(hashtags__name=data) & (Q(group__in=usr_grps) | Q(group=None))
        ).order_by('-date')
    elif page == 'search':
        query = Q(user__username__in=data) & (Q(group__in=usr_grps) | Q(group=None))
        for term in data:
            query |= Q(text__contains=term) | Q(user__username__contains=term)
        db_message_list = Message.objects.filter(query).order_by('-date')
    else:
        db_message_list = Message.objects.filter(pk=page)

    return db_message_list.distinct()


# return Comment List for specific Message
def get_comments(data):
    """

    :param data:
    :return:
    """

    comments = Message.objects.filter(comment=data['message'])
    c = []
    if comments:
        for co in comments:
            cc, ccc = [], get_comments(data={
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


def get_comment_count(message):
    """
    counts comments recursive for a specific message (direct comments and comments of comments)
    :param message: message to get comment count for
    :return: the comment count
    """

    count, comments = 0, Message.objects.filter(comment=message)
    for comment in comments:
        count += get_comment_count(comment) + 1

    return count


def load_more(request):
    """
    loads further messages to current view
    :param request:
    :return: rendered HTML in Template 'message_box_reload.html'
    """

    if not request.user.is_authenticated():                     # check if user is logged in
        return HttpResponseRedirect(reverse("twittur:login"))   # if user is not logged in, redirect to FTU

    data, data_dict = None, request.GET
    page = data_dict.get('page')

    # initialize data dictionary 'context' with relevant display information
    context = get_context(request, page=page, user=request.user)

    # gets specific data to display new messages for different pages
    # cases: 'index, profile, group, search, hashtag'
    if page == 'index':
        data = request.user
    elif page == 'profile':
        data = User.objects.get(username=data_dict['user'])
        context['pUser'] = data
    elif page == 'group':
        data = GroupProfile.objects.get(short=data_dict['group'])
        context['group'] = data
    elif page == 'search':
        data = data_dict['search_input'].split(" ")
        context['search_input'] = data_dict['search_input']
    elif page == 'hashtag':
        data = data_dict.get('hash')
        context['is_hash'] = data_dict['hash']

    messages = get_messages(data={'page': page, 'data': data,
                                  'end': (int(data_dict['length'])+5), 'request': request})

    context['list_length'], context['list_end'] = messages['list_length'], messages['list_end']
    context['has_msg'], context['message_list'] = messages['has_msg'], messages['message_list']

    if 'new_msgs' in messages:
        context['new_msgs'] = messages['new_msgs']

    return render(request, 'message_box_reload.html', context)


def update(request):
    """
    processes request to update a message / comment
    - 'hide_msg', 'hide_cmt':   puts message / comment on message-ignore-list
    - 'del_msg', 'del_cmt':     deletes message / comments and its comments, as well as its picture from the database
    - 'upd_msg':                updates a message / comment with current information
    :param request:
    :return: String with update status
    """

    if not request.user.is_authenticated():                     # check if user is logged in
        return HttpResponseRedirect(reverse("twittur:login"))   # if user is not logged in, redirect to FTU

    data_dict, response = request.GET, None

    # message / comment will be added to user's message-ignore-list
    if data_dict['what'] in ('hide_msg', 'hide_cmt'):
        user_profile = request.user.userprofile
        ignore_list = user_profile.ignoreM.all()
        if Message.objects.filter(pk=data_dict['id']).exists():
            msg = Message.objects.get(pk=data_dict['id'])
            if msg.user in user_profile.ignoreU.all():
                response = "<span class='glyphicon glyphicon-warning'></span>&nbsp;" \
                           "Sie m&uuml;ssen " + msg.user.username + " erst entsperren. Besuchen Sie dazu sein / ihr " \
                           "<a href='" + reverse("twittur:profile", kwargs={'user': msg.user.username}) + \
                           "'>Profil</a>!"
            else:
                if msg in ignore_list:
                    user_profile.ignoreM.remove(msg)
                    response = "<span class='glyphicon glyphicon-ok'></span>&nbsp;" \
                               "Nachricht wird nicht mehr ausgeblendet!"

                else:
                    user_profile.ignoreM.add(msg)
                    response = "<span class='glyphicon glyphicon-ok'></span>&nbsp;" \
                               "Nachricht erfolgreich ausgeblendet!"

    # message / comment and its data (comments, hashtag) will be delete from the database
    elif data_dict['what'] in ('del_msg', 'del_cmt'):
        if Message.objects.filter(pk=data_dict['id']).exists():
            msg = Message.objects.get(pk=data_dict['id'])
            if Message.objects.filter(comment=data_dict['id']).exists():
                comments = Message.objects.filter(comment=msg)
                for obj in comments:
                    hashtaglist = []
                    for hashtag in obj.hashtags.all():
                        hashtaglist.append(hashtag)
                    if hashtaglist:
                        checkhashtag(obj, hashtaglist)
                    obj.delete()
            if msg.picture:
                pic = msg.picture
                pic.delete()
            hashtaglist = []
            for hashtag in msg.hashtags.all():
                hashtaglist.append(hashtag)
            if hashtaglist:
                checkhashtag(msg, hashtaglist)
            msg.delete()
        response = "<span class='glyphicon glyphicon-ok'></span>&nbsp;Nachricht gel&ouml;scht!"

    # message will be updated with current information.
    # may clear the picture and delete it from its folder
    # may change safetyLevel
    elif data_dict['what'] == 'upd_msg':
        if Message.objects.filter(pk=data_dict['id']).exists():
            msg = Message.objects.get(pk=data_dict['id'])
            msg.text = data_dict['val']
            if 'clear' in data_dict and data_dict['clear'] == 'true':
                if msg.picture is not None:
                    pic = msg.picture
                    pic.delete()
                    msg.picture = None
            if 'safety' in data_dict:
                if data_dict['safety'][:1] == '&':
                    group = GroupProfile.objects.get(short__exact=data_dict['safety'][1:])
                elif data_dict['safety'] == 'Public':
                    group = None
                else:
                    group = GroupProfile.objects.get(name__exact=data_dict['safety'])
                msg.group = group
            msg.save()
            msg_to_db(msg)
            response = dbm_to_m(msg).text
    else:
        response = "Something went wrong."

    return HttpResponse(response)


def set_notification(what, data):
    """

    :param what:
    :param data:
    :return:
    """

    ntfc = None
    if what == 'follower':
        ntfc = Notification(user=data['user'], follower=data['follower'], note=data['note'])
    elif what == 'message':
        ntfc = Notification(
            user=data['user'], message=data['message'],
            note='Sie wurden in einer Nachricht erw&auml;hnt.'
        )
    elif what == 'comment':
        ntfc = Notification(user=data['user'], message=data['message'], comment=True, note=data['note'])
    elif what == 'group':
        if 'note' not in data:
            data['note'] = 'Sie wurden aus der Gruppe entfernt.'
        ntfc = Notification(user=data['member'], group=data['group'], note=data['note'])
    elif what == 'group_admin':
        if 'note' not in data:
            data['note'] = 'Sie wurden in der Gruppe ' + data['group'].short + ' zum Admin bef&ouml;rdert.'
        ntfc = Notification(user=data['member'], group=data['group'], note=data['note'])

    ntfc.save()

    return ntfc


def get_notification(request):
    """

    :param request:
    :return:
    """
    context, ntfc_list = {}, []

    if request.method == "POST":
        data_dict = request.POST
    else:
        data_dict = request.GET

    user = data_dict['user'].lower()
    p_user = User.objects.get(username=user)
    p_hash = p_user.userprofile.verifyHash
    if data_dict['hash'] == p_hash:
        ntfc_list_old = Notification.objects.filter(Q(notified=False) & Q(read=False) & Q(user=p_user))
        for ntfc in ntfc_list_old:
            if ntfc.follower:
                ntfc.url = create_abs_url(request, 'profile', ntfc.follower.userprofile.username)
            elif ntfc.group:
                ntfc.url = create_abs_url(request, 'group', ntfc.group.short)
            else:
                ntfc.url = create_abs_url(request, 'message', ntfc.message.id)
            ntfc_list.append(ntfc)
            ntfc.notified = True
            ntfc.save()

    context['ntfc_list'] = ntfc_list
    return render(request, "notification_list.xml", context)


def create_abs_url(request, what, data):
    """

    :param request:
    :param what:
    :param data:
    :return:
    """

    url = None

    if what == 'profile':
        url = reverse("twittur:profile", kwargs={'user': data})
    elif what == 'group':
        url = reverse("twittur:group", kwargs={'groupshort': data})
    elif what == 'message':
        url = reverse("twittur:message", kwargs={'msg': data})

    return request.build_absolute_uri(url)


def get_disciplines():
    """
    generates a list of academicDisciplines in hierarchical order (TU-Berlin -> Fak -> Discipline)
    :return: list of academicDisciplines
    """

    discs, uni, faks = [], [], []

    if GroupProfile.objects.filter(short='uni').exists():
        tub = GroupProfile.objects.get(short='uni')
        fak = GroupProfile.objects.filter(supergroup=tub).order_by('name')
        for item in fak:
            ad = GroupProfile.objects.filter(supergroup=item).order_by('name')
            ad_list = []
            for disc in ad:
                ad_list.append(disc.name)
            faks.append(ad_list)
            uni.append(item.name)
        discs.append(zip(uni, faks))
    return discs


def get_safety_levels(user, group=False):
    """
    generates a list of safety levels
    :param user: current user
    :param group: boolean to check if user groups should be displayed as well
    :return: a list of safety levels for current user
    """

    safety_level = ['Public']

    disc = GroupProfile.objects.get(name=user.userprofile.academicDiscipline)
    fak = GroupProfile.objects.get(name=disc.supergroup)
    uni = GroupProfile.objects.get(name=fak.supergroup)

    safety_level.append(uni)
    safety_level.append(fak)
    safety_level.append(disc)

    if group:
        group_super_list = GroupProfile.objects.filter(pk__in=[24, 25, 34, 35, 36, 37, 38, 39])
        group_list = GroupProfile.objects.filter(
            Q(member__exact=user) & ~Q(pk__in=group_super_list) & ~Q(supergroup__in=group_super_list)
        ).order_by('name')
        gl = []
        for group in group_list:
            gl.append(group)
        safety_level.append(gl)

    return safety_level


def get_faqs():
    """
    creates a list of frequently asked questions
    :return: list of FAQs
    """

    # initialize FAQ list for each category
    faqs, faq_cats = [], FAQ.objects.all().values('category').distinct().order_by('category')
    for cat in faq_cats:
        faq_list = FAQ.objects.filter(category=cat['category']).order_by('question')
        faqs.append(faq_list)

    return faqs


def elim_dups(data):
    """
    eliminates duplicates in a list of messages
    similar to '.distinct()', but this is not usable in our context
    :param data: a message list
    :return:
    """

    dups, final = [], []
    for sub in data:
        for item in sub:
            if item in final:
                dups.append(item)
            else:
                final.append(item)
    return final


def pw_generator(size=6, chars=string.ascii_uppercase + string.digits, hashed=False):
    """
    a random password generator found on http://goo.gl/RH995X
    :param size: length of password
    :param chars: possible chars to be used in generated password
    :return: random generated password
    """

    if hashed:
        m = hashlib.md5()
        m.update((''.join(random.choice(chars) for _ in range(size))).encode('utf-8'))      # extended with md5 hashing
        pw = m.hexdigest()
    else:
        pw = ''.join(random.choice(chars) for _ in range(size))

    return pw


def refresh_hash(request):
    """
    generates a new verify hash for user
    :param request:
    :return: new hash
    """

    if not request.user.is_authenticated():                     # check if user is logged in
        return HttpResponseRedirect(reverse("twittur:login"))   # if user is not logged in, redirect to FTU

    hash_item = pw_generator(hashed=True)
    return HttpResponse(hash_item)


def login_user(request, user):
    """
    snippet found on https://djangosnippets.org/snippets/1547/
    Log in a user without requiring credentials
    (using ``login`` from ``django.contrib.auth``, first finding a matching backend).
    :param request:
    :param user:
    :return:
    """

    from django.contrib.auth import load_backend, login

    if not hasattr(user, 'backend'):
        for backend in settings.AUTHENTICATION_BACKENDS:
            if user == load_backend(backend).get_user(user.pk):
                user.backend = backend
                break

    if hasattr(user, 'backend'):
        return login(request, user)


def verification_mail(request, user):
    """
    sends a verification mail to the user
    :param request:
    :param user:
    :return:
    """

    profile = user.userprofile
    location = reverse("twittur:verify", kwargs={'user': user.username, 'hash_item': profile.verifyHash})
    
    url = request.build_absolute_uri(location)
    message = "Hallo @" + user.username + "!\n" \
              "Ihr Konto bei twittur wurde erstellt." \
              "Bitte verwenden Sie den folgenden Link, um ihr Konto zu aktivieren: \n\n" + url
    
    send_mail("Willkommen bei twittur", message, "twittur.sn@gmail.com", [user.email])


def verify(request, user, hash_item):

    p_user = User.objects.get(username=user)
    p_hash = p_user.userprofile.verifyHash

    if hash_item == p_hash:
        # Only works if user is inactive :-)
        if not p_user.is_active:
            p_user.is_active = True
            p_user.save()
            login_user(request, p_user)
            return HttpResponseRedirect(reverse("twittur:index"))
        else:
            response = "Ihr Account ist bereits aktiv!"
    else:
        response = "Der angegebene Hash stimmt nicht mit dem des Benutzers &uuml;berein."

    return HttpResponse(response)
