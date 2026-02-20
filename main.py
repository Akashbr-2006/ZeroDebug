import os
import subprocess
import shutil
import time
import re
from huggingface_hub import InferenceClient
from dotenv import load_dotenv

# Load environment variables (Make sure HF_TOKEN is in your .env file)
load_dotenv()

# --- CONFIGURATION ---
# Replace with the repository you want to test
REPO_URL = "https://github.com/Akashbr-2006/Bus_Booking_system.git"
TEAM_NAME = "ZERO_DEBUG"
LEADER_NAME = "AKASH_BR"
HF_TOKEN = os.getenv("HF_TOKEN")

client = InferenceClient(token=HF_TOKEN)

def run_command(command, cwd):
    """Executes shell commands and returns the exit code and logs"""
    result = subprocess.run(command, cwd=cwd, shell=True, capture_output=True, text=True)
    return result.returncode, result.stdout + result.stderr

def find_failing_file(logs, workspace):
    """
    Analyzes logs to find which file actually caused the failure.
    """
    # Look for the 'FAILED' line in pytest output
    match = re.search(r'FAILED ([\w\-/]+\.py)', logs)
    if match:
        file_name = match.group(1)
        # Convert path to work on Windows/Linux
        return os.path.normpath(file_name)
    
    # Fallback: scan for any non-test python file if regex fails
    py_files = [f for f in os.listdir(workspace) if f.endswith('.py') and not f.startswith('test_')]
    return py_files[0] if py_files else None

def heal_repo():
    # Setup a clean workspace for this run
    timestamp = int(time.time())
    workspace = os.path.abspath(f"./workspaces/job_{timestamp}")
    os.makedirs(workspace, exist_ok=True)

    # 1. CLONE THE REPOSITORY
    print(f"📡 Cloning {REPO_URL}...")
    clone_code, clone_logs = run_command(f"git clone {REPO_URL} .", workspace)
    if clone_code != 0:
        print(f"❌ Clone failed: {clone_logs}")
        return

    # 2. INSTALL REQUIREMENTS
    if os.path.exists(os.path.join(workspace, "requirements.txt")):
        print("📦 Installing dependencies from requirements.txt...")
        run_command("pip install --quiet -r requirements.txt", workspace)
    
    # Ensure pytest is available for the check
    run_command("pip install --quiet pytest", workspace)

    # 3. THE HEALING LOOP (5 Iterations)
    for i in range(5):
        print(f"🔄 Iteration {i+1}/5: Running Tests...")
        
        # Set PYTHONPATH so pytest can see local modules
        os.environ["PYTHONPATH"] = workspace
        exit_code, logs = run_command("pytest -vv --tb=short", workspace)
        
        if exit_code == 0:
            print("✅ SUCCESS: All tests passed!")
            break
        
        print("❌ Tests failed. Identifying culprit...")

        # 4. DYNAMIC FILENAME DETECTION
        target_file = find_failing_file(logs, workspace)
        if not target_file:
            print("⚠️ Could not identify the failing file. Stopping.")
            break

        file_path = os.path.join(workspace, target_file)
        print(f"🛠️ Auditing {target_file} for bugs...")

        # Read the current bugged code
        with open(file_path, 'r', encoding='utf-8') as f:
            current_code = f.read()

        # 5. GENERATE FIX VIA QWEN-32B
        prompt = (
            f"FIX THE BUG IN THIS CODE.\n\n"
            f"ERROR LOGS:\n{logs}\n\n"
            f"CODE:\n{current_code}\n\n"
            f"INSTRUCTION: Analyze the logs, fix the bug, and return ONLY the full corrected Python code. "
            f"No explanations, no markdown."
        )
        
        try:
            response = client.chat_completion(
                model="Qwen/Qwen2.5-Coder-32B-Instruct",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=2048,
                temperature=0 
            )
            fixed_code = response.choices[0].message.content.strip()

            # Strip markdown if present
            if "```python" in fixed_code:
                fixed_code = fixed_code.split("```python")[1].split("```")[0].strip()
            elif "```" in fixed_code:
                fixed_code = fixed_code.split("```")[1].split("```")[0].strip()

            # 6. APPLY THE FIX
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(fixed_code)
            print(f"Applied fix to {target_file}")

        except Exception as e:
            print(f"⚠️ HuggingFace Error: {str(e)}")
            break

    # 7. COMMIT AND PUSH TO GITHUB
    print("🚀 Pushing fixes to GitHub...")
    branch_name = f"{TEAM_NAME.upper()}_{LEADER_NAME.upper()}_AI_Fix"
    
    run_command(f"git checkout -b {branch_name}", workspace)
    run_command("git add .", workspace)
    run_command(f'git commit -m "[AI-AGENT] Automatically healed logic errors"', workspace)
    
    # Note: Ensure your local Git is authenticated or use a PAT in the URL
    push_code, push_logs = run_command(f"git push -f origin {branch_name}", workspace)
    
    if push_code == 0:
        print(f"🏁 DONE! Branch '{branch_name}' pushed successfully.")
    else:
        print(f"⚠️ Push failed: {push_logs}")

if __name__ == "__main__":
    heal_repo()