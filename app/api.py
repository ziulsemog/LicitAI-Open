import os
from fastapi import FastAPI, Request, HTTPException, Depends
from jose import jwt
import httpx

app = FastAPI(title="LicitAI SaaS API", version="1.0.0")

# Clerk JWKS URL for verifying tokens
CLERK_FRONTEND_API = os.getenv("CLERK_FRONTEND_API")

async def verify_clerk_token(request: Request):
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid Authorization header")
        
    token = auth_header.split(" ")[1]
    
    if not CLERK_FRONTEND_API:
        print("Warning: CLERK_FRONTEND_API is not set. Assuming development mode.")
        return {"sub": "local_dev_user"}
        
    jwks_url = f"https://{CLERK_FRONTEND_API}/.well-known/jwks.json"
        
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(jwks_url)
            response.raise_for_status()
            jwks = response.json()
            
        unverified_header = jwt.get_unverified_header(token)
        rsa_key = {}
        for key in jwks["keys"]:
            if key["kid"] == unverified_header["kid"]:
                rsa_key = {
                    "kty": key["kty"],
                    "kid": key["kid"],
                    "use": key["use"],
                    "n": key["n"],
                    "e": key["e"]
                }
                break
                
        if rsa_key:
            payload = jwt.decode(
                token,
                rsa_key,
                algorithms=["RS256"],
                audience=CLERK_FRONTEND_API,
                issuer=f"https://{CLERK_FRONTEND_API}"
            )
            return payload
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Token verification failed: {str(e)}")
        
    raise HTTPException(status_code=401, detail="Unable to find appropriate key for token verification")

@app.get("/")
def read_root():
    return {"message": "LicitAI SaaS Frontend / API is running."}

@app.get("/api/protected")
def protected_route(user: dict = Depends(verify_clerk_token)):
    return {
        "message": "Autenticado com sucesso no Clerk",
        "user_id": user.get("sub")
    }

@app.get("/api/cron/worker")
async def trigger_worker():
    # Rota chamada via Vercel Cron
    try:
        from workers.worker_pncp import run_worker
        await run_worker()
        return {"status": "success", "message": "Worker de Ingestão executado com sucesso."}
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

async def verify_admin_clerk_token(request: Request):
    user = await verify_clerk_token(request)
    admin_id = os.getenv("ADMIN_USER_ID")
    if not admin_id or user.get("sub") != admin_id:
        raise HTTPException(status_code=403, detail="Acesso negado: Administrador exigido")
    return user

@app.get("/api/admin/stats")
async def admin_stats(user: dict = Depends(verify_admin_clerk_token)):
    from app.services.database import get_admin_stats
    stats = await get_admin_stats()
    return stats

from fastapi.responses import HTMLResponse

@app.get("/admin_dashboard", response_class=HTMLResponse)
async def admin_dashboard_view():
    with open("app/services/dashboard.html", "r") as f:
        html_content = f.read()
    return HTMLResponse(content=html_content)
