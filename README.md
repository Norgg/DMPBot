An irc bot which scans DMPServer logfiles and sends joins/quits and global messages to a channel.

Setup (Ubuntu):

    sudo apt-get install python python-pip
    sudo pip install irc

Single server usage:

    python bot.py irc.esper.net dumpling "#dmptest" DMPServer/logs/ 

Multi server usage:
    python bot.py irc.esper.net dumpling "#dmptest" server1:DMPServer1/logs/ server2:DMPServer2/logs/
