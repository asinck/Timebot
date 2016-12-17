#!/usr/bin/env python

import os
import time, datetime
from slackclient import SlackClient
#from command_handler import *



def printDate():
    return time.strftime("%A, %b %d %Y")

def printTime():
    return time.strftime("%I:%M:%S %p")
    
def whoami(ID):
    return "You are %s." %userlist["%s" %ID]
    #return "I don't know either."


def restart():
    slack_client.api_call("chat.postMessage", channel=channel,
                          text="Restarting Bot...", as_user=True)
    os.execl("timebot.py", '')

def update():
    slack_client.api_call("chat.postMessage", channel=channel,
                          text="Updating Bot...", as_user=True)
    from subprocess import call
    call(["./update.sh"])
    restart()

def showhelp():
    return """Available commands:
```help     : show this help text
time     : show the time
date     : show the date
restart  : restart the bot
quit     : make the bot quit
whoami   : tell you your username
update   : update the bot (includes restart)```"""
#lightrail <direction> : display information about the lightrail timetable, for the given direction. lr is an alias for this.```"""





# starterbot's ID as an environment variable
BOT_ID = os.environ.get("BOT_ID")

# constants
AT_BOT = "<@" + BOT_ID + ">"

#this will be a table of ID:username
userlist = {}


commands = {
    "restart" : restart,
    "help": showhelp,
    "time": printTime,
    "date": printDate,
    "whoami" : whoami,
    "update" : update
}


# instantiate Slack & Twilio clients
slack_client = SlackClient(os.environ.get('SLACK_BOT_TOKEN'))


def handle_command(user, command, channel):
    """
        Receives commands directed at the bot and determines if they
        are valid commands. If so, then acts on the commands. If not,
        returns back what it needs for clarification.
    """
    # response = "Not sure what you mean. Use the *" + EXAMPLE_COMMAND + \
    #            "* command with numbers, delimited by spaces."
    response = "Unrecognized command."
    
    command_token = command.split()[0]

    if (command_token == "quit"):
        slack_client.api_call("chat.postMessage", channel=channel,
                              text="Bye!", as_user=True)
        quit()

    elif (command_token in commands):
        #special cases
        if (command_token == "whoami"):
            response = whoami(user)
        else:
            try:
                response = commands[command_token]()
                #just in case a function forgets to give a response
                if (response == None):
                    response = "No comment."
            except:
                response = "Congratulations, you broke timebot."
            
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
            if output and 'text' in output and AT_BOT in output['text']:
                # return text after the @ mention, whitespace removed
                return output["user"], \
                    output['text'].split(AT_BOT)[1].strip().lower(), \
                    output['channel']
    return None, None, None


if __name__ == "__main__":
    READ_WEBSOCKET_DELAY = 1 # 1 second delay between reading from firehose
    if slack_client.rtm_connect():
        print("Timebot connected and running!\n")

        #populate the list of users
        users = slack_client.api_call("users.list")
        for user in users["members"]:
            userlist[user["id"]] = user["name"]

        while True:
            user, command, channel = parse_slack_output(slack_client.rtm_read())
            if user and command and channel:
                handle_command(user, command, channel)
            time.sleep(READ_WEBSOCKET_DELAY)
    else:
        print("Connection failed. Invalid Slack token or bot ID?")


