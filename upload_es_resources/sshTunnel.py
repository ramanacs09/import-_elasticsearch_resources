from __future__ import print_function
import consoleLogger as consoleLogger
import shlex
import subprocess
import time
import paramiko

# sleep interval for ssh tunnel
createWaitTime = 5
exitWaitTime = 3

logger = consoleLogger.Logger()
logger.createLogHandler(__name__)


def print(msg):
    logger.print(msg)


def createTunnel(tunnelname, localport, remotehost, remoteport, identityfile, user, server, waittime="300s"):
    """Create SSH Tunnels for Database connections"""

    sshTunnelCmd = "ssh -M -o ControlMaster=auto -o ControlPersist=%s -S /tmp/%s -o UserKnownHostsFile=/dev/null " \
                   "-o StrictHostKeyChecking=no -i %s -fnNT -L %s:%s:%s %s@%s" % (
                    waittime, tunnelname, identityfile, localport, remotehost, remoteport, user, server
                   )
    args = shlex.split(sshTunnelCmd)
    tunnel = subprocess.Popen(args)

    time.sleep(createWaitTime)  # Give it a few seconds to finish setting up

    # the program - else the connection will persist
    # after the script ends


def closeSSHTunnel(tunnel, user, server):
    """Close SSH tunnels - given the process handles"""

    sshExitCmd = "ssh -T -O exit -S /tmp/%s %s@%s" % (
        tunnel, user, server
    )

    args = shlex.split(sshExitCmd)
    tunnel = subprocess.Popen(args)

    time.sleep(exitWaitTime)


def createSSHConnection(host, port, user, key):
    '''Uses paramiko to create an SSH connection'''

    sshconnection = paramiko.SSHClient()
    sshconnection.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    print("Connecting.....")
    sshconnection.connect(host, port, username=user, key_filename=key)
    print("Connected.......")

    return sshconnection
