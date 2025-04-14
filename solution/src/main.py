from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, status, Request
from fastapi.exception_handlers import http_exception_handler
from fastapi.middleware.cors import CORSMiddleware
from starlette.formparsers import MultiPartParser

from src.api_v1.campaigns.routes import router as campaigns_router
from src.api_v1.clients.routes import router as clients_router
from src.api_v1.advertisers.routes import router as advertisers_router
from src.api_v1.ads.routes import router as ads_router
from src.api_v1.stats.routes import router as stats_router
from src.api_v1.time.routes import router as time_router
from src.api_v1.ml.routes import router as ml_router
from src.api_v1.files.routes import router as files_router


MultiPartParser.max_file_size = 10 * 1024 * 1024


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield


app = FastAPI(
    root_path="/api/v1",
    lifespan=lifespan,
    debug=False,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/ping")
async def ping():
    return {"message": "prooood"}


@app.exception_handler(ValueError)
async def value_error_exception_handler(request: Request, exc: ValueError):
    return await http_exception_handler(
        request,
        HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ),
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return await http_exception_handler(
        request,
        HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"An error occurred while processing your request. {str(exc)}",
        ),
    )


app.include_router(campaigns_router)
app.include_router(ads_router)
app.include_router(stats_router)
app.include_router(time_router)
app.include_router(clients_router)
app.include_router(advertisers_router)
app.include_router(ml_router)
app.include_router(files_router)
