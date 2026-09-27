from typing import List
from fastapi import WebSocket

# In-memory key state. Fine for a single-instance demo; add persistent
# storage + key rotation before any real deployment.
kem_pk = None
kem_sk = None
dsa_pk = None
dsa_sk = None

active_sockets: List[WebSocket] = []


async def broadcast(message: dict):
    dead = []
    for ws in active_sockets:
        try:
            await ws.send_json(message)
        except Exception:
            dead.append(ws)
    for ws in dead:
        if ws in active_sockets:
            active_sockets.remove(ws)
