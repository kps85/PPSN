__author__ = 'willycai'
# -*- coding: utf-8 -*-
import re

hashtag = "#test #test1 #test2 #testirgendwas"
hashtags = []
attags = []
for word in hashtag.split():
    if word[0] == "#":
        hashtags.append(word)
        #print(word)
    if word[0] == "@":
        attags.append(word)
        #print word

#print hashtags
#print attags


# test for show messages, comments nnd database messeges
'''
messages = ['a', 'b', 'c']
comments = [ ['a', 'b'] , [], ['a', 'b', 'c'] ]
dbmessages = ['x', 'y', 'z']

list = zip(messages,comments)
list2 = zip(messages,comments, dbmessages)
print(list)
print(list2)
for mes, com, dbm in list2:
    print(mes)
    for c in com:
        print(c)
    print(dbm)

# Nachricht definieren (durch das Encoding Cookie als iso-8859-1 gekennzeichnet)
message = "Hallo Österreich"
print(message)


# test for reg ex for hashtags
text = '#test #test1 #test2'

newString = re.sub(r'\B##test', r'yoyoyoyo', text)
print(newString)

hashtag = "This is a #hashtag #test-link #a should#not#work"
x = re.compile(r'\B#\w+')
print x.findall(hashtag)
'''

s = "#test #test1 #test2 #testirgendwas"
variable = '#test2'
href = 'yolo'
s = re.sub(r'(^|\s)%s($|\s)' % re.escape(variable), r'\1%s\2' % href, s)
# print(s)

for word in hashtag.split():
    href = r'<a href="%s">%s</a>' % (word[1:], word)
    hashtag = re.sub(r'(^|\s)%s($|\s)' % re.escape(word), r'\1%s\2' % href, hashtag)

# print(hashtag)

# regex
text = 'äöü'

check = re.findall(r'[a-zA-Z0-9-_äöüßÄÖÜ]+', text[1:])
print(text[1:] in check)
print(type(text))

print text.decode('UTF-8')
text2 = '\xc3\xb6'
print text2.decode('utf-8')