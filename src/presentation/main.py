from fastapi import FastAPI

app = FastAPI(title="TeamUp endpoint")

@app.get("/")
def health_check():
    return {"message": "I am alive. Welcome to the app!"}