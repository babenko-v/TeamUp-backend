from fastapi import FastAPI

from presentation.dependencies import init_dependencies

from presentation.auth.router import router as auth_router
from presentation.projects.router import router as project_router


app = FastAPI(title="TeamUp endpoint", prefix="/api/v1")

init_dependencies(app)
app.include_router(auth_router)
app.include_router(project_router)

@app.get("/")
def health_check():
    return {"message": "I am alive. Welcome to the app!"}