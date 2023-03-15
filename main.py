import uvicorn
from fastapi import FastAPI

from apps import routes
from config import settings

app = FastAPI(
    title=settings.PROJECT_NAME,
    description=settings.PROJECT_DESCRIPTION,
    version=settings.PROJECT_VERSION
)


@app.on_event('startup')
def startup_event():
    # models.Base.metadata.drop_all(engine)
    # models.Base.metadata.create_all(engine)
    app.include_router(routes.user)
    app.include_router(routes.auth)


@app.on_event('shutdown')
def shutdown_event():
    pass


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
