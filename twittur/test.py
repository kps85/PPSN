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
print attag