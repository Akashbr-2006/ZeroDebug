import subprocess

class GitManager:
    def __init__(self, workspace_path, team_name, leader_name):
        self.path = workspace_path
        self.branch_name = f"{team_name.upper()}_{leader_name.upper()}_AI_Fix"

    def _run(self, args):
        return subprocess.run(["git"] + args, cwd=self.path, capture_output=True, text=True)

    def prepare_branch(self):
        self._run(["checkout", "-B", self.branch_name])

    def commit_and_push(self, message):
        full_msg = f"[AI-AGENT] {message}"
        self._run(["add", "."])
        self._run(["commit", "-m", full_msg])
        self._run(["push", "--set-upstream", "origin", self.branch_name])