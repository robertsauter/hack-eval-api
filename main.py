from fastapi import FastAPI, Request
from routers import users
from fastapi.middleware.cors import CORSMiddleware
from jose import ExpiredSignatureError, jwt
from lib.globals import SECRET_KEY, ALGORITHM
from fastapi.responses import JSONResponse

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=['http://localhost:5173'],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware('http')
async def check_if_token_expired(request: Request, call_next):
    auth = request.headers.get('Authorization')
    if auth:
        token = auth.split(' ', maxsplit=1)[1]        
        try:
            jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        except ExpiredSignatureError:
            return JSONResponse('Token expired', 403)
    response = await call_next(request)
    return response

app.include_router(users.router, prefix='/users')