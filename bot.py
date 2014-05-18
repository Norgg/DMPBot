import sys, os, re
from irc.bot import SingleServerIRCBot

class DMPBot(SingleServerIRCBot):
    def __init__(self, logdir, channel, nick, server, port=6667):
        super(DMPBot, self).__init__([(server, port)], nick, nick)
        self.server = server
        self.channel = channel

        self.logdir = logdir
        self.logfile = None
        self.logdir_modified = 0

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
        if (os.path.getmtime(self.logdir) > self.logdir_modified):
            self.logdir_modified = os.path.getmtime(self.logdir)
            logs =  [os.path.join(self.logdir, f) for f in os.listdir(self.logdir) if os.path.isfile(os.path.join(self.logdir, f))]
            latest_log = max(logs, key=os.path.getmtime)
            if latest_log != self.logfile:
                print("Following logfile: %s" % latest_log)
                self.logfile = latest_log
                self.log = open(self.logfile, 'r')
                self.log.seek(os.stat(self.logfile)[6]) # seek to end

        where = self.log.tell()
        line = self.log.readline()
        if line:
            #print(line)

            joinmatch = self.joinre.match(line)
            quitmatch = self.quitre.match(line)
            disconnmatch = self.disconnre.match(line)
            globalmatch = self.globalre.match(line)
            if joinmatch:
                self.connection.privmsg(self.channel, "%s joined the server" % joinmatch.group(1))
            elif quitmatch:
                self.connection.privmsg(self.channel, "%s quit" % quitmatch.group(1))
            elif disconnmatch:
                self.connection.privmsg(self.channel, "%s disconnected: %s" % (disconnmatch.group(1), disconnmatch.group(3)))
            elif globalmatch:
                self.connection.privmsg(self.channel, "%s: %s" % (globalmatch.group(1), globalmatch.group(2)))
                
        else:
            self.log.seek(where)

if __name__ == "__main__":
    if len(sys.argv) < 5:
        print("Error: Not enough arguments.")
        print("usage: <logdir> <server[:port]> <nick> <channel>")
        sys.exit(1)
    
    logdir = sys.argv[1]

    server = sys.argv[2].split(":", 1)
    server_name = server[0]
    
    if len(server) == 2:
        try:
            server_port = int(server[1])
        except ValueError:
            server_port = 6667
    else:
        server_port = 6667
    
    nick = sys.argv[3]
    channel = sys.argv[4]

    bot = DMPBot(logdir, channel, nick, server_name, server_port)
    bot.start()
