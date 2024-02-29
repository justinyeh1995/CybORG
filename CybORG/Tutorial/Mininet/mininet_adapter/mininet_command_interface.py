import pexpect
from Mininet.utils.util import parse_action, get_all_matches

class MininetCommandInterface:
    def __init__(self):
        self.mininet_process = None

    def start_mininet(self, topology_file: str) -> s:
        self.mininet_process = pexpect.spawn(f"sudo python3 Mininet/mininet_utils/custom_net.py -y {topology_file}")
        self.mininet_process.timeout = 300
        self.mininet_process.expect("mininet>")
        return self.mininet_process.before.decode()

    def send_command(self, command: str) -> str:
        if self.mininet_process and self.mininet_process.isalive():
            self.mininet_process.sendline(command)
            self.mininet_process.expect('mininet>')
            return self.mininet_process.before.decode()
        return "Mininet process is not running."

    def stop_mininet(self) -> None:
        if self.mininet_process and self.mininet_process.isalive():
            self.mininet_process.terminate()
            self.mininet_process.expect(pexpect.EOF)
