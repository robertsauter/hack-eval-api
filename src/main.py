from fastapi import FastAPI, Request, APIRouter
from src.routers import users, hackathons, analyses, filters
from fastapi.middleware.cors import CORSMiddleware
from jose import ExpiredSignatureError, jwt
from src.lib.globals import SECRET_KEY, ALGORITHM
from fastapi.responses import JSONResponse

app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None)

app.add_middleware(
    CORSMiddleware,
    allow_origins=['https://demo.colaps.team'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

app_router = APIRouter()

app_router.include_router(users.router, prefix='/users')
app_router.include_router(hackathons.router, prefix='/hackathons')
app_router.include_router(analyses.router, prefix='/analyses')
app_router.include_router(filters.router, prefix='/filters')

app.include_router(app_router, prefix='/hackpulseapi')


@app.middleware('http')
async def check_if_token_expired(request: Request, call_next):
    '''This is run before every request. If the request contains a token, check if it expired'''
    auth = request.headers.get('Authorization')
    if auth and auth.startswith('Bearer'):
        token = auth.split(' ', maxsplit=1)[1]
        try:
            jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        except ExpiredSignatureError:
            return JSONResponse('Token expired', 403)
    response = await call_next(request)
    return response
