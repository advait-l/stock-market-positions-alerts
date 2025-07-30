from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import stocks

app = FastAPI()

origins = [
    "http://localhost:3000",
    "https://localhost:3000",
    "https://*.vercel.app",
    "https://*.netlify.app",
    # Add your production domain here
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(stocks.router, prefix="/api")

@app.get("/")
def read_root():
    return {"message": "Welcome to the Stock Market Positions Alerts API"}

# Vercel handler function
def handler(request, response):
    return app
