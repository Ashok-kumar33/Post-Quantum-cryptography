import io
from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import StreamingResponse
from .. import state
from ..crypto_core import protect_bytes, recover_bytes

router = APIRouter(prefix="/files", tags=["files"])


@router.post("/encrypt")
async def encrypt_file(file: UploadFile = File(...)):
    if not state.kem_pk:
        raise HTTPException(400, "Generate keys first")
    data = await file.read()
    blob = protect_bytes(data, state.kem_pk, state.dsa_sk)
    await state.broadcast({
        "type": "log",
        "message": f"Encrypted {file.filename} ({len(data)} bytes)",
    })
    return StreamingResponse(
        io.BytesIO(blob),
        media_type="application/octet-stream",
        headers={"Content-Disposition": f"attachment; filename={file.filename}.pqsafe"},
    )


@router.post("/decrypt")
async def decrypt_file(file: UploadFile = File(...)):
    if not state.kem_sk:
        raise HTTPException(400, "Generate keys first")
    blob = await file.read()
    try:
        data = recover_bytes(blob, state.kem_sk, state.dsa_pk)
    except Exception as e:
        raise HTTPException(400, f"Decryption/verification failed: {e}")
    name = file.filename.replace(".pqsafe", "") or "recovered.bin"
    await state.broadcast({
        "type": "log",
        "message": f"Decrypted {file.filename} ({len(data)} bytes)",
    })
    return StreamingResponse(
        io.BytesIO(data),
        media_type="application/octet-stream",
        headers={"Content-Disposition": f"attachment; filename={name}"},
    )
