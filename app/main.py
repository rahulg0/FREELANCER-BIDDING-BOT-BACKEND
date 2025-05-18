from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import bidding

app = FastAPI(
    title="Bidding Bot Backend",
    description="API Backend for Freelancer Bidding Bot.",
    version="1.0.0"
)



app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Freelancer Bid Bot"}

app.include_router(bidding.router)
