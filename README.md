#Timebot

This is a bot for Slack. Most of what it does is teach me how to program Slack bots.

To run a command, directly address the bot (ie, `@timebot whoami`) or use a ! (ie, `!whoami`).

The following commands can be used
- help: This will show a list of commands the user can use.
- time: This will show the current time.
- date: This will show the current date.
- restart: This will restart the bot.
- quit: This will cause the bot to leave.
- whoami: This will tell the user who they are. This is mostly just so that I know the bot can do this.
- list: This will handle shopping lists. This command follows the syntax `!list command [item(s)] [listName(s)]`. There are multiple commands that can be used:
  - view listname - This shows the contents of the specified list.
  - list - this gives a list of lists.
  - clear listname - clear the contents of the specified list.
  - add/remove item(s) listname - add or remove the specified items (separated by commas) from the specified list.
  - merge lists listname - merge all specified lists into the specified list.
  - rename list1 list2 - rename list1 as list2.
  - delete listname - delete a list.

