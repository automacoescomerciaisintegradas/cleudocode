import os
import subprocess
import threading
import time

# AIDEV-NOTE: Bridge python server control for launching and monitoring the Electron Desktop Application
class CleudocodeDesktopBridge:
    """Manages the lifecycle of the Cleudocode Native Desktop Client from Python processes."""
    
    def __init__(self, workspace_path="/root/cleudocode"):
        self.workspace_path = workspace_path
        self.app_dir = os.path.join(self.workspace_path, "cleudocode-desktop")
        self.process = None
        self.thread = None
        self.is_running = False

    def _monitor_output(self, pipe, prefix):
        """Reads stream output asynchronously to avoid blocking and logs it."""
        try:
            for line in iter(pipe.readline, ''):
                if line:
                    # You could tie this to standard application logging instead of stdout
                    print(f"[{prefix}] {line.strip()}")
        except Exception as e:
            print(f"[{prefix} Stream Closed]: {str(e)}")
        finally:
            pipe.close()

    def launch(self, daemon=True):
        """
        Launches the Electron Desktop Application via npm start.
        Args:
            daemon (bool): Runs the app in a background thread if True. Blocking otherwise.
        """
        if not os.path.isdir(self.app_dir):
            raise FileNotFoundError(f"Desktop client application not found at: {self.app_dir}. Ensure scaffold was completed.")

        print(f"🚀 Initializing Cleudocode Desktop Bridge to -> {self.app_dir}")

        if daemon:
            self.thread = threading.Thread(target=self._run_subprocess, daemon=True)
            self.thread.start()
            # Give it some startup time
            time.sleep(2)
            if self.is_running:
                print("✅ Desktop Client spawned successfully in background.")
            else:
                print("⚠️ Desktop Client spawn check failed (might still be spinning up).")
        else:
            self._run_subprocess()

    def _run_subprocess(self):
        """Executes the actual command."""
        self.is_running = True
        try:
            # We use bash to properly source node/npm environments if needed in WSL
            command = "npm run start"
            
            self.process = subprocess.Popen(
                command,
                cwd=self.app_dir,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                universal_newlines=True
            )

            # Start thread monitors for STDOUT and STDERR to avoid buffer death
            stdout_thread = threading.Thread(target=self._monitor_output, args=(self.process.stdout, "ELECTRON-STDOUT"), daemon=True)
            stderr_thread = threading.Thread(target=self._monitor_output, args=(self.process.stderr, "ELECTRON-STDERR"), daemon=True)
            
            stdout_thread.start()
            stderr_thread.start()

            # Block until process completes (if running as daemon, this only blocks the thread)
            self.process.wait()
            
        except Exception as e:
            # AIDEV-ERR: Catch issues with process elevation or missing binaries
            print(f"❌ Failed to run Desktop Bridge subprocess: {e}")
        finally:
            self.is_running = False
            print("📴 Desktop Client Process Terminated.")

    def stop(self):
        """Gracefully or forcefully attempts to bring down the app."""
        if self.process and self.is_running:
            print("🛑 Stopping Cleudocode Desktop Application...")
            self.process.terminate()
            try:
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                print("⚠️ Process did not close in 5s. Killing forcefully.")
                self.process.kill()
            self.is_running = False
            self.process = None

# Testing or standalone execution
if __name__ == "__main__":
    bridge = CleudocodeDesktopBridge()
    try:
        # Run blocking to see output directly
        bridge.launch(daemon=False)
    except KeyboardInterrupt:
        bridge.stop()
        print("Exiting bridge manager.")
