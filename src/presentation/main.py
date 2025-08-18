from fastapi import FastAPI

from presentation.auth.router import auth_router

app = FastAPI(title="TeamUp endpoint", prefix="/api")

app.include_router(auth_router)

@app.get("/")
def health_check():
    return {"message": "I am alive. Welcome to the app!"}