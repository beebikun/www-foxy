import sys
import paramiko


class UpdateServerSSH(object):
    proj = '/var/www/tlvx'

    def __init__(self, argv):
        self.in_proj = False
        try:
            self.pswd = argv['p']
            self.open(argv['h'], argv['u'], self.pswd, argv.get('port', 22))
            self.move2proj()
        except KeyError:
            self._intstruction()

    def _instruction(self):
        print 'Use: python update.py -p PSWD -u LGN -h HOST [-port PORT]'
        raise SystemExit

    def open(self, h, u, p, port):
        self.client = paramiko.SSHClient()
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.client.connect(hostname=h, username=u, password=p, port=port)

    def sudo(self, cmd):
        stdin, stdout, stderr = self.client.exec_command("sudo -S %s" % cmd)
        stdin.write('%s\n' % self.pswd)
        stdin.flush()
        return stdout.read() + stderr.read()

    def move2proj(self):
        self.sudo('cd %s' % self.proj)

    def update(self):
        self.sudo('./update.sh')

    def close(self):
        self.client.close()


def get_argv():
    raw = ' '.join(sys.argv[1:]).split('-')
    argv = dict([[i for i in a.split(' ') if i] for a in raw if a])
    return argv


def update_server():
    server = UpdateServerSSH(get_argv())
    server.update()
    server.close()


if __name__ == "__main__":
    update_server()
