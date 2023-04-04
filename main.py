import logging
from types import NoneType
from typing import Optional

import uvicorn
from fastapi import FastAPI, APIRouter
from fastapi.responses import UJSONResponse
from starlette import status

from apps import routes
from config.celery_utils import create_celery
from config.es_connector import ES_connect
from config.settings import settings

app = FastAPI(
    title=settings.PROJECT_NAME,
    description=settings.PROJECT_DESCRIPTION,
    version=settings.PROJECT_VERSION
)

app.celery_app = create_celery()
celery = app.celery_app

elastic_route = APIRouter()

es = ES_connect()  # connect to elastic
log = logging.getLogger("uvicorn")


@elastic_route.get("/elastic/get/", tags=["Elasticsearch"], description="Get a document with all DB fields.")
async def get(keywords: Optional[str]):
    response = await es.search_document(query=keywords)
    if type(response) == NoneType or len(response) == 0:
        return UJSONResponse(status_code=status.HTTP_404_NOT_FOUND,
                             content="Your keywords did not match any documents! Try changing the keywords")
    return response


@elastic_route.post("/fillingES", tags=["Elasticsearch"],
                    description="Filling the Elastic with data from the database.")
async def filling():
    log.info("Initialize filling Elastic from DB...")
    await es.populate_es()
    log.info("Finish filling Elastic.")
    return status.HTTP_200_OK


@app.on_event('startup')
async def startup_event():
    # models.Base.metadata.drop_all(engine)
    # models.Base.metadata.create_all(engine)
    app.include_router(elastic_route)
    app.include_router(routes.post)
    app.include_router(routes.auth)
    app.include_router(routes.user)


if __name__ == "__main__":
    uvicorn.run(app, host='0.0.0.0', port=8000)
