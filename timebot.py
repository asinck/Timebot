#!/usr/bin/env python

import os
import time, datetime
from slackclient import SlackClient
#from command_handler import *

shoppingList = {}

#work with shopping lists
def shopping(commands):
    #commands will be in the format
    # list command [item] listName
    # - list is the command to activate this function
    # - command (view|list|add|remove|clear|merge|delete):
    #    - view items in the list
    #    - list what lists you have
    #    - add or remove a given item from a specified list
    #    - clear a specified list
    #    - merge all lists into the last
    #    - delete a list
    # - item is an argument for add or remove
    # - listname is the name of the list

    #this merges two lists
    def merge(l1, l2):
        a = set(l1)
        b = set(l2)
        return sorted(list(a.union(b)))
    
    tokens = [str(i) for i in commands.split()]
    command = ""
    if (len(tokens) > 1):
        command = tokens[1]

    response = ""

    if (len(tokens) == 1 or command not in ["view", "list", "add", "remove", "clear", "merge", "delete", "help"]):
        response = "Invalid command. Use `\list help` for available commands."

    elif (command == "help"):
        response = """```list command [item] [listName]
- list is the command to activate this function
- command (view|list|add|remove|clear|merge|delete):
   - view items in the list
   - list what lists you have
   - add or remove the given item(s) from a specified list
   - clear a specified list
   - merge all lists into the last
   - delete a list
- item is an argument for add or remove
- listname is the name of the list```"""


    elif (command == "view"):
        listname = tokens[-1]
        if (listname in shoppingList):
            if (shoppingList[listname] == []):
                response = "List %s is empty." %listname
            else:
                response = "Contents of %s:\n```%s```" %(listname, '\n'.join(shoppingList[listname]))
        else:
            response = "List %s does not exist." %listname
        

    elif (command == "list"):
        if (len(shoppingList) == 0):
            response = "No lists."
        else:
            response = ", ".join([name for name in shoppingList])

    elif (command in ["add", "remove"]):
        if (len(tokens) < 4):
            response = "You need to specify what to add/remove to which list."
        else:
            listname = tokens[-1]
            #get all items listed
            items = tokens[2:len(tokens)-1]
            if (command == "add"):
                if (listname not in shoppingList):
                    shoppingList[listname] = []
                shoppingList[listname] = merge(items, shoppingList[listname])
                response = "%s added to %s." %(', '.join(items), listname)
            else: #(command == "remove")
                if (listname not in shoppingList):
                    response = "List %s does not exist."
                else:
                    shoppingList[listname] = [item for item in shoppingList[listname] if item not in items]
                    response = "%s removed from %s." %(', '.join(items), listname)
            

    elif (command == "clear"):
        listname = tokens[-1]
        if (listname in shoppingList):
            shoppingList[listname] = []
            response = "List %s cleared." %listname
        else:
            response = "List %s does not exist." %listname
        
    elif (command == "merge"):
        if (len(tokens) < 4):
            response = "You need to specify at least two lists to merge."
        else:
            listname = tokens[-1]
            mergedLists = []
            failedLists = []
            if (listname not in shoppingList):
                shoppingList[listname] = []
            for name in tokens[2:len(tokens)-1]:
                if name in shoppingList:
                    mergedLists.append(name)
                    shoppingList[listname] = merge(shoppingList[listname], shoppingList[name])
                else:
                    failedLists.append(name)

            if (len(failedLists) == 0):
                response = "Lists merged into list %s." %listname
            else:
                response = "%s merged into list %s,\n%s failed to merge." \
                           %(', '.join(mergedLists), listname, ', '.join(failedLists))


    elif (command == "delete"):
        listname = tokens[-1]
        if (listname in shoppingList):
            del(shoppingList[listname])
            response = "List %s deleted." %listname
        else:
            response = "List %s does not exist." %listname


    return response

def saveLists():
    listFile = open("lists.txt", "w")
    lists = ""
    for listName in shoppingList:
        lists += listName + ":" + " ".join(shoppingList[listName]) + "\n"
    lists = lists.strip()
    listFile.write(lists)
    listFile.close()
        

#this is a function to print the date    
def printDate():
    return time.strftime("%A, %b %d %Y")

#this is a function to print the time
def printTime():
    return time.strftime("%I:%M:%S %p")
    
#this is a function to tell you who you are. This is mainly for testing if I can do this.
def whoami(ID):
    return "You are %s." %userlist["%s" %ID]
    #return "I don't know either."

#this function restarts the bot.
def restart():
    slack_client.api_call("chat.postMessage", channel=channel,
                          text="Restarting Bot...", as_user=True)
    
    saveLists()
    os.execl("timebot.py", '')

#this function pulls updates from github and then restarts the bot.
#This may cause issues if there are unpushed changes in the repo though.
def update():
    slack_client.api_call("chat.postMessage", channel=channel,
                          text="Updating Bot...", as_user=True)
    from subprocess import call
    call(["./update.sh"])
    restart()

#this shows available commands.
def showhelp():
    return """Available commands:
```help     : show this help text
time     : show the time
date     : show the date
restart  : restart the bot
quit     : make the bot quit
whoami   : tell you your username
list     : work with shopping lists. Use `\list help` for details. ```"""
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
    "time"    : printTime,
    "date"    : printDate,
    "whoami"  : whoami,
    "list"    : shopping
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
        saveLists()
        quit()

    elif (command_token in commands):
        #special cases
        if (command_token == "whoami"):
            response = whoami(user)
        elif (command_token == "list"):
            response = shopping(command)
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
            if (output and 'text' in output):
                if (output['text'].find(AT_BOT) == 0):
                    # return text after the @ mention, whitespace removed
                    return output["user"], \
                        output['text'].split(AT_BOT)[1].strip().lower(), \
                        output['channel']
                
                elif (output['text'][0] == '!'):
                    # return text after the \, whitespace removed
                    return output["user"], \
                        output['text'][1:].strip().lower(), \
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

        
        #load the lists
        if (not os.path.isfile("lists.txt")):
            listFile = open("lists.txt", "w+")
            listFile.close()

        #this reads a file for restoring lists
        listFile = open("lists.txt", "r")
        for line in listFile:
            listName, items = line.strip().split(":")
            shoppingList[listName] = items.split()
        listFile.close()
        

        while True:
            user, command, channel = parse_slack_output(slack_client.rtm_read())
            if user and command and channel:
                handle_command(user, command, channel)
            time.sleep(READ_WEBSOCKET_DELAY)
    else:
        print("Connection failed. Invalid Slack token or bot ID?")


