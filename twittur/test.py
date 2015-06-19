__author__ = 'willycai'


hashtag = "hello #yolo #jvpj #wbvbeu @yolo @halo"
hashtags = []
attags = []
for word in hashtag.split():
    if word[0] == "#":
        hashtags.append(word)
        print(word)
    if word[0] == "@":
        attags.append(word)
        print word

print hashtags
print attags


# test for show messages, comments nnd database messeges

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