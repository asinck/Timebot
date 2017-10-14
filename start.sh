#!/bin/sh
virtualenv starterbot;
source starterbot/bin/activate;
export BOT_ID="$BOT_ID";
export SLACK_BOT_TOKEN="$SLACK_BOT_TOKEN";
export BIBLE_BOT_ID="$BIBLE_BOT_ID";
export BIBLE_SLACK_BOT_TOKEN="$BIBLE_SLACK_BOT_TOKEN";
./timebot.py;
