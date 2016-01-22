#!/usr/bin/env python
# -*- coding: utf-8 -*-
import argparse
import os
import json

from pymongo import MongoClient

class LogImporter(object):
    def __init__(self, data, constring):
        self.data_dir = data
        self.db = MongoClient(constring).get_default_database()
        self.messages = self.db.messages

        self.channels = self.__load_channels()
        self.channel_ids = {chan["name"]: chan["id"] for chan in self.channels}

        self.users = self.__load_users()
        self.user_names = {user["id"]: user["name"] for user in self.users}


    def __load_channels(self):
        chan_file = os.path.join(self.data_dir, "channels.json")
        f = open(chan_file)
        channels = json.load(f)
        f.close()
        return channels

    def __load_users(self):
        user_file = os.path.join(self.data_dir, "users.json")
        f = open(user_file)
        users = json.load(f)
        f.close()
        return users


    def channel(self, chan):
        def insert_messages(msgs):
            if len(msgs) == 0:
                return
            self.messages.insert(msgs)

        def insert_chunk(filename):
            f = open(filename)
            msgs = json.load(f)
            f.close()
            for msg in msgs:
                msg["channel"] = self.channel_ids[chan]
                msg["channel_name"] = chan

                if "user" not in msg:
                    continue

                if msg["user"] == "USLACKBOT":
                    msg["user_name"] = "slackbot"
                elif msg["user"] in self.user_names:
                    msg["user_name"] = self.user_names[msg["user"]]
                else:
                    msg["user_name"] = "unknown"

            insert_messages(msgs)

        chan_dir = os.path.join(self.data_dir, chan)
        if not (os.path.exists(chan_dir) and os.path.isdir(chan_dir)):
            raise ValueError("Channel could not be found in the log directory")

        for filename in os.listdir(chan_dir):
            insert_chunk(os.path.join(chan_dir, filename))

    def all_channels(self):
        chans = [f for f in os.listdir(self.data_dir)
                 if os.path.isdir(os.path.join(self.data_dir, f))]
        for chan in chans:
            self.channel(chan)

def main():
    parser = argparse.ArgumentParser(description="Import Slack logs into MongoDB")
    parser.add_argument("--logs", required=True, type=str, metavar="LOGDIR", help="Directory containing Slack log files")
    parser.add_argument("--mongo", required=True, type=str, metavar="MONGOCON", help="MongoDB connection string")
    args = parser.parse_args()

    importer = LogImporter(data=os.path.realpath(args.logs), constring=args.mongo)
    importer.all_channels()

if __name__ == "__main__":
    main()
