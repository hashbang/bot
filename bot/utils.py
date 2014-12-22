""" Various IRC / Bot utility functions. """

def parsemsg(line):
    """
    Breaks a message from an IRC server into its prefix, command, and
    arguments. Returns a dict with those (as well as 'raw' for original text)
    Taken from twisted irc.
    """

    prefix = ''
    trailing = []
    if not line:
        return {}
    s = line
    if s[0] == ':':
        prefix, s = s[1:].split(' ', 1)
    if s.find(' :') != -1:
        s, trailing = s.split(' :', 1)
        args = s.split()
        args.append(trailing)
    else:
        args = s.split()
    command = args.pop(0)

    msg = {
       'prefix' : prefix,
       'command': command,
       'args'   : args,
       'raw'    :  line
    }

    return annotatemsg(msg)

def annotatemsg(msg):
    """
    Depending on command type will add useful properties to msg object.
    """

    command = msg['command']

    if command == 'PRIVMSG':
        args = msg['args']
        nick = msg['prefix'].split('!')[0]
        chan = args[0]
        parts = args[1].split(' ')

        msg.update({
            'nick'  : nick,
            'chan'  : chan,
            'cmd'   : parts[0],
            'terms' : ' '.join(parts[1:]).strip(),
        })

    return msg

def log(msg, *args):
    """
    Colored logging.
    """
    msg = msg.format(*args) +" "
    first, rest = msg.split(" ",1)
    print("\033[33m{}\033[0m {}".format(first, rest))

class RecordedSock:
    def __init__(self, sock, filename):
        self.sock = sock
        if filename == "-":
            import sys
            self.stream = sys.stdout
        else:
            self.stream = open(filename, "w")

    def send(self, message):
        print("<" + message.decode('utf-8').encode('unicode_escape').decode('ascii'), file = self.stream)
        self.sock.send(message)

    def recv(self, count):
        message = self.sock.recv(count)
        print(">" + message.decode('utf-8').encode('unicode_escape').decode('ascii'), file = self.stream)
        return message

    def __del__(self):
        self.stream.flush()

def connect(config):
    """ Connect to
    config['host'] on port config['port'] (default 6667)

    if config["RecordNetData"] has been set, record network data to that file.
    """

    import socket
    sock = socket.socket()
    sock.connect((config['host'], config.get('port', 6667))) # Default port 6667

    if config.get("RecordNetData", ""):
        sock = RecordedSock(sock, config.get("RecordNetData"));

    return sock

def messageIterator(socket):
    """ Given a socket, read data from it and yield each complete message
    This removes the trailing \r\n.
    """
    read = ""
    try:
        while True:
            data = socket.recv(1024)
            if not data:
                return

            read += data.decode('utf-8')
            lines = read.split("\r\n")
            lines, read = lines[:-1],lines[-1]

            for line in lines:
                yield parsemsg(line)

    except KeyboardInterrupt:
        log("Keyboard interrupt")
        return


