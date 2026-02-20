from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from orchestrator import run_healing_cycle
import json

app = FastAPI()

@app.websocket("/ws/agent")
async def run_agent_ws(websocket: WebSocket):
    await websocket.accept()
    
    try:
        # 1. Wait for React to send the repo URL
        data = await websocket.receive_json()
        repo_url = data.get("repo_url")
        
        # 2. Define the hook that pushes data LIVE to React
        async def live_update_hook(message: str):
            # We send a JSON object that React can easily parse
            await websocket.send_json({
                "type": "log_update",
                "message": message
            })

        # 3. Start the healing cycle and pass our WebSocket hook
        await websocket.send_json({"type": "log_update", "message": "Agent initialized. Starting process..."})
        
        # Run your existing orchestrator
        await run_healing_cycle(repo_url, live_update_hook)
        
        await websocket.send_json({"type": "completed", "message": "Process finished!"})

    except WebSocketDisconnect:
        print("Frontend disconnected.")