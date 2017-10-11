#!/usr/bin/env python

# This bot has two functionalities:
#  - view the title of the current xkcd
#  - view an xkcd comic
#    - if given no arguments, the current comic
#    - if given a number, the numbered comic

import os, time, datetime
from slackclient import SlackClient
import lxml.html as web
from urllib2 import urlopen


# xkcdbot's ID as an environment variable
BOT_ID = os.environ.get("BOT_ID")

# Constants
AT_BOT = "<@" + BOT_ID + ">"

# These are commands the user can do.
commands = {
    "help"    : showhelp,
    "xkcd"    : xkcd,
    "viewxkcd": viewxkcd
}

# Instantiate Slack client
slack_client = SlackClient(os.environ.get('SLACK_BOT_TOKEN'))


# Return the formatted date    
def printDate(args = []):
    return time.strftime("%A, %b %d %Y")

# Return the formatted time
def printTime(args = []):
    return time.strftime("%I:%M:%S %p")

# Return the title of the current xkcd comic.
def xkcd(args = []):
    return web.parse(urlopen("https://xkcd.com/")).find(".//title").text

# This shows the user the current xkcd. It relies on Slack to expand
# the image URL to show the image
def viewxkcd(args = []):
    page = None
    try:
        if (args == []):
            page = urlopen("https://xkcd.com/")
        else:
            page = urlopen("https://xkcd.com/" + args[0] + "/")

        # Fetch the source
        doc = web.parse(page)
        title = "_*" + doc.find(".//title").text + "*_"
        matches = doc.xpath("//img")
        imgsrc = ""
        alt = ""

        # Get the image and alt text
        for match in matches:
            if "imgs.xkcd.com/comics/" in match.get('src'):
                imgsrc = "https:" + match.get('src')
                alt = "_" + match.get('title') + "_"
                break

        # Make sure nothing is null
        if "" not in [title, imgsrc, alt]:
            return "%s\n%s\n%s" %(imgsrc, title, alt)
        else:
            return "Could not obtain comic information."
    
    # In case there's an issue, such as a 404
    except Exception as error:
        return str(error)


# Return available commands.
def showhelp():
    return """Available commands:
```help     : show this help text
quit     : make the bot quit
xkcd     : get the title of the latest xckd
viewxkcd : view the current xkcd + alt text```"""


# This handles the user commands. 
def handle_command(user, command, channel):
    """
        Receives commands directed at the bot and determines if they
        are valid commands. If so, then acts on the commands. If not,
        returns back what it needs for clarification.
    """
    response = "Unrecognized command."
    
    command_token = command.split()[0]

    if (command_token == "quit"):
        slack_client.api_call("chat.postMessage", channel=channel,
                              text="Bye!", as_user=True)
        quit()

    elif (command_token in commands):
        try:
            response = commands[command_token](command.split()[1:])
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


