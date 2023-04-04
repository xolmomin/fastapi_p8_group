from fastapi import APIRouter, Depends
from fastapi.responses import UJSONResponse
from sqlalchemy.orm import Session
from starlette import status

from apps import models
from apps.services import get_current_activate_user
from celery_tasks.post import delete_all_post_worker, generate_posts
from config.db import get_db

post = APIRouter(tags=['post'], prefix='/api')


@post.post('/posts')
async def add_post(n: int):
    generate_posts.delay(n)
    return {'message': f'Successfully added posts !'}


@post.delete('/delete/{pk}', summary='Delete a post')
async def delete_all_post(
        pk: int,
        db: Session = Depends(get_db),
        current_user=Depends(get_current_activate_user)
):
    result = db.query(models.Post).filter_by(id=pk, author_id=current_user.id).delete()
    db.commit()
    if result:
        return UJSONResponse({'message': 'Successfully deleted !'})
    return UJSONResponse({'message': 'Not found post'}, status.HTTP_404_NOT_FOUND)


@post.delete('/delete', summary='Delete all posts')
async def delete_all_post():
    delete_all_post_worker.delay()
    return {'message': 'Successfully deleted !'}
