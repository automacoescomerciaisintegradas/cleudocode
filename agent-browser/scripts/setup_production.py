import os
import subprocess
import sys
import platform

def run_command(command):
    print(f"Executing: {command}")
    try:
        subprocess.run(command, shell=True, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error executing command: {e}")
        return False
    return True

def setup_production():
    print("🚀 Starting Production Setup for CleudoCode Browser Agent...")
    
    # 1. Install Python Dependencies
    print("\n📦 Installing Python dependencies...")
    if not run_command("pip install playwright pytest-playwright"):
        return

    # 2. Install Browser Binaries
    print("\n🌐 Installing Chromium browser...")
    if not run_command("playwright install chromium"):
        return

    # 3. Linux Specific: Install System Dependencies
    if platform.system() == "Linux":
        print("\n🐧 Linux detected: Installing system dependencies...")
        run_command("playwright install-deps chromium")

    # 4. Environment Sanity Check
    print("\n🔍 Checking environment...")
    cli_path = os.path.join(os.getcwd(), "agent-browser", "agent_browser_cli.py")
    if os.path.exists(cli_path):
        print(f"✅ CLI Script found at: {cli_path}")
    else:
        print(f"❌ CLI Script NOT found at: {cli_path}")

    print("\n✨ Production Setup Complete!")
    print("You can now run the agent using: python agent-browser/agent_browser_cli.py IA open <url>")

if __name__ == "__main__":
    setup_production()
