from twisted.internet import protocol
from twisted.python import log
from twisted.words.protocols import irc


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
            log.msg('Your nickname was already occupied, actual nickname is ''"{}".'.format(self.nickname))
        self.join(self.factory.channel)

    def joined(self, channel):
        """Called when the bot joins the channel."""
        log.msg("[{nick} has joined {channel}]".format(nick=self.nickname, channel=self.factory.channel,))

    def privmsg(self, user, channel, msg):
        """Called when the bot receives a message."""
        sendTo = channel
        msg = msg.lower()
        for trigger in self.factory.triggers:
            if msg in trigger:
                break

        if sendTo:
            message = "Hello team!"
            self.msg(sendTo, message)
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
