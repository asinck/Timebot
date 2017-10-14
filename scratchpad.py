import lxml.html as web
import urllib2
import json

url = "https://bible-api.com/john%203:16-4:19"
result = urllib2.urlopen(url).read()
# print result

output = ""
parsed = json.loads(result)
output += parsed["reference"]
output += "\n"

# Get the initial chapter
chapter = parsed["verses"][0]["chapter"]

# Go through all the verses
for verse in parsed["verses"]:
    
    if (verse["chapter"] != chapter):
        chapter = verse["chapter"]
        output += "\n" + str(chapter) + "\n"

    output += str(verse["verse"]) + " "
    output += verse["text"].strip().replace("\n", " ") + "\n"

print output

