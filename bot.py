import sys, os, re
from irc.bot import SingleServerIRCBot

class DMPBot(SingleServerIRCBot):
    def __init__(self, logdirs, channel, nick, server, port=6667):
        super(DMPBot, self).__init__([(server, port)], nick, nick)
        self.server = server
        self.channel = channel

        self.joinre = re.compile(r".* Client (.*?) handshook successfully!.*")
        self.quitre = re.compile(r".*: (.*?) sent connection end message, reason: (.*)")
        self.disconnre = re.compile(r".* Client (.*?) disconnected, endpoint (.*?), error: (.*)")
        self.globalre = re.compile(r".*: (.*?) -> #Global: (.*)")
        print("DMPBot connecting to %s:%s" % (server, port))

    def on_nicknameinuse(self, connection, e):
        connection.nick(connection.get_nickname() + "_")

    def on_welcome(self, connection, event):
        print("Connected to %s, joining %s" % (self.server, self.channel))
        connection.join(self.channel)

    def on_join(self, connection, event):
        self.connection.execute_every(0.1, self.checklog)

    def checklog(self):
        for logdir in logdirs:
            line = logdir.check()
            if line:
                #print(line)
                joinmatch = self.joinre.match(line)
                quitmatch = self.quitre.match(line)
                disconnmatch = self.disconnre.match(line)
                globalmatch = self.globalre.match(line)
                if joinmatch:
                    self.msg(logdir.tag, "%s joined the server" % joinmatch.group(1))
                elif quitmatch:
                    self.msg(logdir.tag, "%s quit" % quitmatch.group(1))
                elif disconnmatch:
                    self.msg(logdir.tag, "%s disconnected: %s" % (disconnmatch.group(1), disconnmatch.group(3)))
                elif globalmatch:
                    self.msg(logdir.tag, "%s: %s" % (globalmatch.group(1), globalmatch.group(2)))
    def msg(self, tag, message):
        if tag:
            message = "%s - %s" % (tag, message)
        self.connection.privmsg(self.channel, message)
        


class LogDir(object):
    def __init__(self, tag, path):
        self.last_modified = 0
        self.path = path
        self.tag = tag
        self.logfile = None
        

    def check(self):
        if (os.path.getmtime(self.path) > self.last_modified):
            self.last_modified = os.path.getmtime(self.path)
            logs =  [os.path.join(self.path, f) for f in os.listdir(self.path) if os.path.isfile(os.path.join(self.path, f))]
            latest_log = max(logs, key=os.path.getmtime)
            if latest_log != self.logfile:
                print("Following logfile: %s" % latest_log)
                self.logfile = latest_log
                self.log = open(self.logfile, 'r')
                self.log.seek(os.stat(self.logfile)[6]) # seek to end

        where = self.log.tell()
        line = self.log.readline()
        if not line:
            self.log.seek(where)
        return line
        

if __name__ == "__main__":
    if len(sys.argv) < 5:
        print("Error: Not enough arguments.")
        print("usage: <server[:port]> <nick> <channel> <[tag:]logdir>*")
        sys.exit(1)
    
    args = list(sys.argv[1:]) # Take a copy of argv

    server = args.pop(0).split(":", 1)
    server_name = server[0]
    
    if len(server) == 2:
        try:
            server_port = int(server[1])
        except ValueError:
            server_port = 6667
    else:
        server_port = 6667
    
    nick = args.pop(0)
    channel = args.pop(0)

    # Any remaining args are logdirs
    logdirs = []
    for d in args:
        dtoks = d.split(":", 1)
        if len(dtoks) == 2:
            logdirs.append(LogDir(dtoks[0], dtoks[1]))
        else:
            logdirs.append(LogDir(None, d))

    bot = DMPBot(logdirs, channel, nick, server_name, server_port)
    bot.start()
