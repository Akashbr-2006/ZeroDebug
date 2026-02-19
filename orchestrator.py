import os, time
from agent import ZeroDebugAgent
from sandbox import SandboxManager
from git_manager import GitManager

def run_healing_cycle(repo_url, log_hook):
    TEAM, LEADER = "ZERO_DEBUG", "AKASH_BR"
    agent = ZeroDebugAgent(TEAM, LEADER)
    sandbox = SandboxManager()
    job_id = f"job_{int(time.time())}"
    
    log_hook(f"Cloning {repo_url}...")
    workspace = sandbox.clone_repo(repo_url, job_id)
    git = GitManager(workspace, TEAM, LEADER)
    git.prepare_branch()
    
    results = []
    # TARGET_FILE: Since we are in 'Atomic' mode, we target the main logic file
    target_file = "calculator.py" 
    file_path = os.path.join(workspace, target_file)

    for i in range(5):
        log_hook(f"Iteration {i+1}/5: Testing...")
        run = sandbox.run_tests_in_docker(workspace)
        
        if run["status"] == "PASSED":
            log_hook("✅ SUCCESS: All tests passed.")
            break
            
        log_hook(f"❌ Tests failed. Sending {target_file} to AI for healing...")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            current_code = f.read()
        
        fixed_code = agent.generate_fix(run["logs"], current_code)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(fixed_code)
        
        results.append({"iteration": i+1, "file": target_file})

    if results:
        log_hook("Pushing fixes to GitHub...")
        git.commit_and_push("AI-powered healing cycle completed")
    
    return results