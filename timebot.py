#!/usr/bin/env python

import os, time
from slackclient import SlackClient
import lists, functions


# #this clears the old messages. This is because the bot had some sort of caching issue.
# def flush_buffer():
#     user, command, channel, timestamp = parse_slack_output(slack_client.rtm_read())
#     now = time.time() + 1
#     print "Clearing messages before %f" %now
#     while (not timestamp or (timestamp and float(timestamp) < now)):
#         user, command, channel, timestamp = parse_slack_output(slack_client.rtm_read())
#         print "Clearing %s : %s" %(str(timestamp), command)


#this function restarts the bot.
def restart():
    slack_client.api_call("chat.postMessage", channel=channel,
                          text="Restarting Bot...", as_user=True)
    
    lists.saveLists()
    os.execl("timebot.py", '')

#this function pulls updates from github and then restarts the bot.
#This may cause issues if there are unpushed changes in the repo though.
def update():
    slack_client.api_call("chat.postMessage", channel=channel,
                          text="Updating Bot...", as_user=True)
    from subprocess import call
    call(["./update.sh"])
    restart()

#this is a function to tell you who you are. This is mainly for testing if I can do this.
def whoami(ID):
    return "You are %s." %userlist["%s" %ID]
    #return "I don't know either."


#this shows available commands.
def showhelp():
    return """Available commands:
```help     : show this help text
time     : show the time
date     : show the date
restart  : restart the bot
quit     : make the bot quit
whoami   : tell you your username
list     : work with lists. Use `!list help` for details. ```"""
#update   : update the bot (includes restart)

#lightrail <direction> : display information about the lightrail timetable, for the given direction. lr is an alias for this.```"""


# starterbot's ID as an environment variable
BOT_ID = os.environ.get("BOT_ID")

# constants
AT_BOT = "<@" + BOT_ID + ">"

#this will be a table of ID:username
userlist = {}

#these are commands the user can do. update is currently disabled due to possible issues with git.
commands = {
    "restart" : restart,
    "help"    : showhelp,
    "whoami"  : whoami,
    "time"    : functions.printTime,
    "date"    : functions.printDate,
    "list"    : lists.handle_commands
    #"update" : update
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
        lists.saveLists()
        quit()

    elif (command_token in commands):
        #special cases
        if (command_token == "whoami"):
            response = whoami(user)
        elif (command_token == "list"):
            response = lists.handle_commands(channel, command)
        else:
            try:
                response = commands[command_token]()
            except:
                response = "Congratulations, you broke timebot."
            
    #just in case a function forgets to give a response
    if (response == None):
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
                        output['channel']
                
                elif (output['text'][0] == '!'):
                    # return text after the !, whitespace removed
                    return output["user"], \
                        output['text'][1:].strip().lower(), \
                        output['channel'], \
                        output['ts']
                
                    
    return None, None, None, None


if __name__ == "__main__":
    READ_WEBSOCKET_DELAY = 0.5 # number of seconds to delay between reading from firehose

    PROGRAM_START = time.time() #time the program started

    print "Program started at %f." %PROGRAM_START

    if slack_client.rtm_connect():
        print("Timebot connected and running!\n")

        #populate the list of users
        users = slack_client.api_call("users.list")
        for user in users["members"]:
            userlist[user["id"]] = user["name"]

        channel_list = slack_client.api_call("channels.list")
        for channel in channel_list["channels"]:
            slack_client.api_call("channels.mark")
            print "Marked all messages as read in channel %s" %channel["name"]

        lists.restore_lists()

        # print "Clearing old messages..."
        # flush_buffer()
        # print "Finished."

        while True:
            user, command, channel, timestamp = parse_slack_output(slack_client.rtm_read())
            # print (whoami(user) if user else user), command, channel, timestamp
            # if timestamp:
            #     print "message before timestamp?", float(timestamp) < PROGRAM_START
            if user and command and channel and timestamp and float(timestamp) > PROGRAM_START:
                handle_command(user, command, channel)
            time.sleep(READ_WEBSOCKET_DELAY)
    else:
        print("Connection failed. Invalid Slack token or bot ID?")


