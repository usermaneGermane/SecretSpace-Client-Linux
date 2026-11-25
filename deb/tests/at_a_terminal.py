"""
CI: run a command at a terminal of its own and answer its password prompt.

    python3 at_a_terminal.py PASSWORD COMMAND [ARGUMENT ...]
"""

import os
import pty
import select
import sys
import time

password, command = sys.argv[1], sys.argv[2:]
pid, terminal = pty.fork()
if pid == 0:
    os.execvp(command[0], command)
seen, answered, end = b"", False, time.time() + 60
while time.time() < end:
    if select.select([terminal], [], [], 1)[0]:
        try:
            piece = os.read(terminal, 1024)
        except OSError:                     # Linux: the other end is closed
            break
        if not piece:
            break
        seen += piece
        # Only now: a hidden prompt throws away what was typed before it.
        if not answered and b"assword" in seen:
            time.sleep(0.5)
            os.write(terminal, password.encode() + b"\n")
            answered = True
else:
    print(seen)
    sys.exit("it did not finish")
print(seen.decode(errors="replace"))
if password.encode() in seen:
    sys.exit("the password was shown")
status = os.waitpid(pid, 0)[1]
sys.exit(os.waitstatus_to_exitcode(status) if answered else "it did not ask")
