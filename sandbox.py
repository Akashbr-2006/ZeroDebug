import os
import shutil
import stat
import docker
from git import Repo

def remove_readonly(func, path, _excinfo):
    os.chmod(path, stat.S_IWRITE)
    func(path)

class SandboxManager:
    def __init__(self):
        self.docker_client = docker.from_env()
        self.workspace_root = os.path.abspath("./agent_workspaces")
        os.makedirs(self.workspace_root, exist_ok=True)

    def clone_repo(self, repo_url: str, job_id: str) -> str:
        job_dir = os.path.join(self.workspace_root, job_id)
        if os.path.exists(job_dir):
            shutil.rmtree(job_dir, onerror=remove_readonly)
        Repo.clone_from(repo_url, job_dir)
        return job_dir

    def run_tests_in_docker(self, workspace_path: str) -> dict:
        # 1. Install local requirements if they exist
        # 2. Force PYTHONPATH so local imports work
        # 3. Run pytest with maximum detail for the AI
        full_command = (
            'sh -c "if [ -f requirements.txt ]; then pip install --quiet -r requirements.txt; fi && '
            'pip install --quiet pytest && '
            'export PYTHONPATH=$PYTHONPATH:. && '
            'pytest -vv --tb=long ."'
        )
        
        try:
            output = self.docker_client.containers.run(
                image="python:3.11-slim",
                command=full_command,
                volumes={workspace_path: {'bind': '/app', 'mode': 'rw'}},
                working_dir="/app",
                environment={"PYTHONUNBUFFERED": "1"},
                remove=True,
                stdout=True,
                stderr=True
            )
            return {"status": "PASSED", "logs": output.decode('utf-8')}
        except docker.errors.ContainerError as e:
            # Capture the full detailed traceback for Qwen-32B
            return {
                "status": "FAILED", 
                "logs": e.stderr.decode('utf-8') if e.stderr else "Execution Error"
            }