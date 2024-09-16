from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import auth, bidding

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
    return {"message": "Hello World"}

app.include_router(auth.router)
app.include_router(bidding.router)
