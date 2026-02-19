from fastapi import FastAPI, BackgroundTasks
from pydantic import BaseModel
import uuid, time
from orchestrator import run_healing_cycle

app = FastAPI()
jobs = {}

class RepoRequest(BaseModel):
    repo_url: str

@app.post("/heal")
async def start_healing(request: RepoRequest, background_tasks: BackgroundTasks):
    job_id = str(uuid.uuid4())
    jobs[job_id] = {"status": "Starting", "logs": []}
    background_tasks.add_task(healing_task, job_id, request.repo_url)
    return {"job_id": job_id}

@app.get("/status/{job_id}")
def get_status(job_id: str):
    return jobs.get(job_id, {"status": "Not Found"})

def healing_task(job_id, repo_url):
    def log_it(msg):
        jobs[job_id]["logs"].append(f"[{time.strftime('%H:%M:%S')}] {msg}")
        print(msg)

    jobs[job_id]["status"] = "Processing"
    try:
        results = run_healing_cycle(repo_url, log_it)
        jobs[job_id]["status"] = "Completed"
    except Exception as e:
        jobs[job_id]["status"] = "Failed"
        log_it(f"CRITICAL ERROR: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)