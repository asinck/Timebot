#!/usr/bin/env python

# This bot lets a user look up bible verses, using the
# https://bible-api.com/ API.

import os, time, datetime
from slackclient import SlackClient
import urllib2, json

# xkcdbot's ID as an environment variable
BOT_ID = os.environ.get("BOT_ID")

# Constants
AT_BOT = "<@" + BOT_ID + ">"

# instantiate Slack client
slack_client = SlackClient(os.environ.get('SLACK_BOT_TOKEN'))


# Return the formatted date    
def printDate(args = []):
    return time.strftime("%A, %b %d %Y")

# Return the formatted time
def printTime(args = []):
    return time.strftime("%I:%M:%S %p")


# Return the verses. 
def getVerses(passage):
    if (passage == ""):
        return "What verse(s)?"

    try:
        passage = passage.replace(" ", "+")

        url = "https://bible-api.com/%s" %passage
        result = urllib2.urlopen(url).read()

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

        return output

    # In case there's an issue, such as a 404
    except Exception as error:
        with open("error.txt", 'w+') as log:
                log.write("%s %s: Web error token = %s\n" %(printDate(), printTime(), str(error)))
                
                log.write("\nError input: %s %s" %(version, passage))
        if (str(error).strip() == "HTTP Error 404: Not Found"):
            return str(error) + "\nCheck your command formatting maybe?"
        else:
            return str(error)


# Return available commands. This omits the quit command, which
# standard users don't need to know. If I was ambitious, I would add
# privilege checking.
def showhelp():
    return """The following commands are available. This uses the https://bible-api.com/ API. Only the KJV bible is currently supported. 

```
help, h     : show this help text
bible, b    : Look up a verse
```

Example commands:
`!help`
`!b John 3:16`
`!bible Genesis 1`

If it gives you an error, check your formatting and if the reference is valid. Note that the bot is relatively easy to confuse.
"""


# This handles the user commands. 
def handle_command(user, command, channel):
    """
        Receives commands directed at the bot and determines if they
        are valid commands. If so, then acts on the commands. If not,
        returns back what it needs for clarification.
    """
    response = "Unrecognized command."
    
    command_token = command.split()[0]

    if (command_token in ["quit", "q"]):
        slack_client.api_call("chat.postMessage", channel=channel,
                              text="Bye!", as_user=True)
        quit()

    elif (command_token in ["help", "h"]):
        response = showhelp()
        

    elif (command_token in ["bible", "b"]):
        try:
            response = getVerses(' '.join(command.split()[1:]))
        except:
            with open("error.txt", 'w+') as error:
                error.write("%s %s: Error token = %s\n" %(printDate(), printTime(), command_token))
            response = "Error parsing command."

    
    #just in case a function forgets to give a response
    if (response in [None, ""]):
        response = "No comment."
    slack_client.api_call("chat.postMessage", channel=channel,
                          text=response, as_user=True)


def parse_slack_output(slack_rtm_output):
    """
        The Slack Real Time Messaging API is an events firehose.
        this parsing function returns None unless a message is
        directed at the Bot, based on its ID.
    """
    output_list = slack_rtm_output
    if output_list and len(output_list) > 0:
        for output in output_list:
            if (output and 'text' in output):
                if (output['text'].find(AT_BOT) == 0):
                    # return text after the @ mention, whitespace removed
                    return output["user"], \
                        output['text'].split(AT_BOT)[1].strip().lower(), \
                        output['channel'], \
                        output['ts']
                
                elif (output['text'][0] == '!'):
                    # return text after the !, whitespace removed
                    return output["user"], \
                        output['text'][1:].strip().lower(), \
                        output['channel'], \
                        output['ts']
                
                    
    return None, None, None, None


if __name__ == "__main__":
    PROGRAM_START = time.time() #time the program started
    print "Program started at %f." %PROGRAM_START

    READ_WEBSOCKET_DELAY = 0.5 # number of seconds to delay between reading from firehose

    if slack_client.rtm_connect():
        print("Timebot connected and running!\n")

        channel_list = slack_client.api_call("channels.list")
        for channel in channel_list["channels"]:
            slack_client.api_call("channels.mark")
            print "Marked all messages as read in channel %s" %channel["name"]

        # Parse until further notice
        while True:
            user, command, channel, timestamp = parse_slack_output(slack_client.rtm_read())

            if user and command and channel and timestamp and float(timestamp) > PROGRAM_START:
                handle_command(user, command, channel)

            time.sleep(READ_WEBSOCKET_DELAY)
    else:
        print("Connection failed. Invalid Slack token or bot ID?")


