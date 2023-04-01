from fastapi import APIRouter

from apps.services.post import generate_posts, delete_all_post_worker

post = APIRouter(tags=['post'])


@post.post('/posts')
async def add_post(n: int):
    generate_posts.delay(n)
    return {'message': f'Successfully added posts !'}


@post.delete('/delete')
async def delete_all_post():
    delete_all_post_worker.delay()
    return {'message': 'Successfully deleted !'}
