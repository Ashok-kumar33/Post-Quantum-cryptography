from fastapi import APIRouter, HTTPException
from .. import state
from ..crypto_core import generate_keys

router = APIRouter(prefix="/keys", tags=["keys"])


@router.post("/generate")
async def generate():
    state.kem_pk, state.kem_sk, state.dsa_pk, state.dsa_sk = generate_keys()
    await state.broadcast({
        "type": "log",
        "message": f"Generated ML-KEM-1024 ({len(state.kem_pk)}B pk) "
                    f"and ML-DSA-65 ({len(state.dsa_pk)}B pk) keys",
    })
    return {
        "kem_pk_size": len(state.kem_pk),
        "kem_sk_size": len(state.kem_sk),
        "dsa_pk_size": len(state.dsa_pk),
        "dsa_sk_size": len(state.dsa_sk),
    }


@router.get("/export")
async def export_bundle():
    if not state.kem_pk:
        raise HTTPException(400, "Generate keys first")
    return {
        "kem_pk": state.kem_pk.hex(),
        "dsa_pk": state.dsa_pk.hex(),
        "config": {"version": "2.0", "standard": "FIPS 203/204"},
    }
