import pexpect
import traceback 
import inspect
from CybORG import CybORG, CYBORG_VERSION

class MininetCommandInterface:
    def __init__(self):
        self.mininet_process = None

    
    def start_mininet(self, topology_file: str) -> str:
        self.clean()
        path = str(inspect.getfile(CybORG))
        path = path[:-7] + f'/Tutorial/Mininet/mininet_utils/custom_net.py'
        self.mininet_process = pexpect.spawn(f"sudo python3 {path} -y {topology_file}")
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
            print("Terminated the ongoing Mininet topology.")


    def clean(self) -> None:
        # First, ensure that the existing Mininet subprocess is terminated
        try:
            # First, check if a Mininet process is running and terminate it
            self.stop_mininet()
            
            # Now, run the Mininet cleanup command
            cleanup_process = pexpect.spawn("sudo mn -c")
            cleanup_process.timeout = 60
            cleanup_process.expect(pexpect.EOF)  # Wait for the end of the process
            print("Cleaned up the topology successfully")
            # print(cleanup_process.before.decode())

        except Exception as e:
            print("An error occurred while cleaning up the topology:")
            print(str(e))

        finally:
            if cleanup_process is not None and cleanup_process.isalive():
                cleanup_process.terminate()