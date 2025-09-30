from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database.engine_db import Base, engine
from routes import cities_routes, hotels_routes, evaluations_routes

Base.metadata.create_all(bind=engine)

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

app.include_router(cities_routes.router)
app.include_router(hotels_routes.router)
app.include_router(evaluations_routes.router)

@app.get("/")
async def read_root():
    return {"message": "Welcome to the Pocket GO API!"}

@app.get("/health")
async def health_check():
    return {"status": "ok"}