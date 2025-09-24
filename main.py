from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Pocket GO API",
    description="API for the Pocket GO project",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],  
    allow_headers=["*"],
    expose_headers=["*"] 
)

@app.get("/")
async def read_root():
    return {"message": "Welcome to the Pocket GO API!"}

@app.get("/health")
async def health_check():
    return {"status": "ok"}