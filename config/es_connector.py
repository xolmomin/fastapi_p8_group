"""
Connect Elasticsearch.
&
Search document.
"""
from elasticsearch import AsyncElasticsearch, Elasticsearch
from elasticsearch.helpers import bulk
from sqlalchemy import desc
from sqlalchemy.orm import Session

from apps.models import Post
from config.db import get_db


class ES_connect:
    def __init__(self) -> None:
        self.es_client = None
        self.connect()

    def connect(self):
        """Connect Elastic.."""
        es = AsyncElasticsearch("http://localhost:9200")
        self.es_client = es

    async def search_document(self, index="posts", query="Hello world!"):
        """
        Search document from index by text and sort by created date ...
        """
        try:
            # response = await self.es_client.search(
            #     index="posts",
            #     body={
            #         "from": 0, "size": 20,
            #         "query": {
            #             "match": {
            #                 "text": query
            #             }
            #         },
            #         # "sort": "created_at"
            #     }
            # )

            # res = []
            # result = [res.append(hit["_source"]) for hit in response["hits"]["hits"]]
            # return res

            response = await self.es_client.search(index="posts", body={"query": {"multi_match": {"query": query}}})
            return [i['_source'] for i in response['hits']['hits']]
        except Exception as e:
            print(e)

    async def populate_es(self):
        """
        Filling Elasticsearch with data from the database on the server.
        """
        db: Session = next(get_db())
        posts = db.query(Post).order_by(desc(Post.created_at)).all()
        for post in posts:
            e1 = {
                'id': post.id,
                'title': post.title,
                'description': post.description,
            }

            await self.es_client.index(index='posts', id=post.id, document=e1)

# mashina(nomi, brand, hajmi, narxi),
# notebook(nomi,price, ram)
# odam (ismi, yoshi, address)
