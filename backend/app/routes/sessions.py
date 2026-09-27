from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from .. import state

router = APIRouter(tags=["sessions"])


@router.websocket("/ws/sessions")
async def sessions_ws(websocket: WebSocket):
    await websocket.accept()
    state.active_sockets.append(websocket)
    await websocket.send_json({"type": "log", "message": "Connected to QuantumSafe backend"})
    try:
        while True:
            await websocket.receive_text()  # keep-alive; content from client is ignored
    except WebSocketDisconnect:
        if websocket in state.active_sockets:
            state.active_sockets.remove(websocket)
