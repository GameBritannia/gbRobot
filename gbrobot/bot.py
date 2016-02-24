import json
import pytz
import requests
from datetime import datetime
from dateutil import parser
from random import randint
from twisted.internet import protocol
from twisted.python import log
from twisted.words.protocols import irc


def get_response(message, user=None):
    user = user.split('!')[0]

    # MMR
    if message == "!mmr":
        return user + " your mmr is: " + str(randint(0, 9999))

    # Giveaway
    elif message == "!giveaway":
        return "We're giving away 3 pairs of tickets to PC Gamers Weekender on March 5th-6th in London: http://bit.ly/24pBx8D"

    # Social
    elif message == "!social":
        return "Follow us at http://twitter.com/GameBritannia, like us at http://facebook.com/GameBritannia & don't forget to follow!"

    # Rules
    elif message == "!rules":
        return "Standins: Allowed as long as they study at that University"

    # Uptime
    elif message == "!uptime":
        r = requests.get("https://api.twitch.tv/kraken/streams/gamebritannia")
        if r.status_code == 200:
            response = r.json()
            if response["stream"] is not None:
                uptime = datetime.now(pytz.utc) - parser.parse(response["stream"]["created_at"])
                return "GameBritannia has been streaming for: " + str(uptime.days) + " days, " + str(uptime.seconds) + " seconds."
            else:
                return "GameBritannia is offline. Check back later!"
        else:
            return "Could not retrieve uptime"
    else:
        return None


class GBRobot(irc.IRCClient):
    def connectionMade(self):
        self.nickname = self.factory.nickname
        self.realname = self.factory.realname
        self.password = self.factory.password
        irc.IRCClient.connectionMade(self)
        log.msg("connectionMade")

    def connectionLost(self, reason):
        irc.IRCClient.connectionLost(self, reason)
        log.msg("connectionLost {!r}".format(reason))

    def signedOn(self):
        """Called when bot has successfully signed on to server."""
        log.msg("Signed on")
        if self.nickname != self.factory.nickname:
            log.msg('Name taken, new is ''"{}".'.format(self.nickname))
        self.join(self.factory.channel)

    def joined(self, channel):
        """Called when the bot joins the channel."""
        log.msg("GbRobot joined " + self.factory.channel)

    def privmsg(self, user, channel, incoming_message):
        """Called when the bot receives a message."""
        sendTo = channel
        incoming_message = incoming_message.lower()

        if sendTo:
            response = get_response(incoming_message, user)
            if response:
                self.msg(sendTo, response)
                log.msg(
                    "sent message to {receiver}, triggered by {sender}:\n\t{quote}"
                    .format(receiver=sendTo, sender=sendTo, quote=None)
                )


class GBRobotFactory(protocol.ClientFactory):

    protocol = GBRobot

    def __init__(self, channel, nickname, realname, password, triggers):
        """Initialise the bot"""
        self.channel = channel
        self.nickname = nickname
        self.realname = realname
        self.password = password
        self.triggers = triggers
