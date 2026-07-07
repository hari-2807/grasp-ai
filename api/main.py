from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from api.routers import upload, agent, auth, payments


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Grasp API starting up...")
    yield
    print("Grasp API shutting down...")


app = FastAPI(
    title="Grasp API",
    description="Upload anything. Understand everything.",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"detail": "Something went wrong. Please try again."},
    )


@app.get("/health")
def health_check():
    return {"status": "ok"}


app.include_router(upload.router)
app.include_router(agent.router)
app.include_router(auth.router)
app.include_router(payments.router)
