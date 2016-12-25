import os

lists = {}


#work with lists
def handle_commands(commands):
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
    
    #tokens = [str(i) for i in commands.split()]
    tokens = commands.split()
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
        if (listname in lists):
            if (lists[listname] == []):
                response = "List %s is empty." %listname
            else:
                response = "Contents of %s:\n```%s```" %(listname, '\n'.join(lists[listname]))
        else:
            response = "List %s does not exist." %listname
        

    elif (command == "list"):
        if (len(lists) == 0):
            response = "No lists."
        else:
            response = ", ".join([name for name in lists])

    elif (command in ["add", "remove"]):
        if (len(tokens) < 4):
            response = "You need to specify what to add/remove to which list."
        else:
            listname = tokens[-1]
            #get all items listed
            items = tokens[2:len(tokens)-1]
            #this next command changes the splitting from on whitespace to on commas
            items = [i.strip() for i in " ".join(items).split(",")]
            if (command == "add"):
                if (listname not in lists):
                    lists[listname] = []
                lists[listname] = merge(items, lists[listname])
                response = "%s added to %s." %(', '.join(items), listname)
            else: #(command == "remove")
                if (listname not in lists):
                    response = "List %s does not exist."
                else:
                    lists[listname] = [item for item in lists[listname] if item not in items]
                    response = "%s removed from %s." %(', '.join(items), listname)
            

    elif (command == "clear"):
        listname = tokens[-1]
        if (listname in lists):
            lists[listname] = []
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
            if (listname not in lists):
                lists[listname] = []
            for name in tokens[2:len(tokens)-1]:
                if name in lists:
                    mergedLists.append(name)
                    lists[listname] = merge(lists[listname], lists[name])
                else:
                    failedLists.append(name)

            if (len(failedLists) == 0):
                response = "Lists merged into list %s." %listname
            else:
                response = "%s merged into list %s,\n%s failed to merge." \
                           %(', '.join(mergedLists), listname, ', '.join(failedLists))


    elif (command == "delete"):
        listname = tokens[-1]
        if (listname in lists):
            del(lists[listname])
            response = "List %s deleted." %listname
        else:
            response = "List %s does not exist." %listname


    return response

def saveLists():
    listFile = open("lists.txt", "w")
    listsString = ""
    for listName in lists:
        listsString += listName + "\t" + " ".join(lists[listName]) + "\n"
    listsString = listsString.strip()
    listFile.write(listsString)
    listFile.close()

def restore_lists():
    #load the lists
    if (not os.path.isfile("lists.txt")):
        listFile = open("lists.txt", "w+")
        listFile.close()

    #this reads a file for restoring lists
    listFile = open("lists.txt", "r")
    for line in listFile:
        listName, items = line.strip().split("\t")
        lists[listName] = [i.strip() for i in items.split(",")]
    listFile.close()

