from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from database.engine_db import Base, engine
from routes import (
    users_routes,
    cities_routes,
    hotels_routes,
    evaluations_routes,
    hotel_details_routes,
    logs_routes,
    room_types_routes, 
    rate_plans_routes, 
    room_prices_routes
)

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Pocket GO API",
    description="API for the Pocket GO project",
    version="1.0.1",
)

# Mount static files FIRST - before any middleware that might interfere
app.mount("/static", StaticFiles(directory="static"), name="static")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],  
    allow_headers=["*"],
    expose_headers=["*"] 
)

app.include_router(users_routes.router)
app.include_router(cities_routes.router)
app.include_router(hotels_routes.router)
app.include_router(hotel_details_routes.router)
app.include_router(evaluations_routes.router)
app.include_router(logs_routes.router)

# These routes are for new funcionalitys that are currently in development
app.include_router(room_types_routes.router)
app.include_router(rate_plans_routes.router)
app.include_router(room_prices_routes.router)

@app.get("/")
async def read_root():
    return {"message": "Welcome to the Pocket GO API!"}

@app.get("/favicon.ico")
async def favicon():
    """Return 204 No Content for favicon requests to avoid 404 errors"""
    # this will be here for the tests right now
    from fastapi import Response
    return Response(status_code=204)

@app.get("/health")
async def health_check():
    return {"status": "ok"}