import uvicorn
from fastapi import FastAPI
from fastapi_limiter import FastAPILimiter
import redis.asyncio as redis
from fastapi.middleware.cors import CORSMiddleware

from src.routes import auth, contacts, users
from src.config.config import settings

app = FastAPI()

app.include_router(auth.router, prefix='/api')
app.include_router(contacts.router, prefix='/api')
app.include_router(users.router, prefix='/api')

@app.on_event('startup')
async def startup():
    """
    The startup function is called when the server starts up.
    It's a good place to initialize things that are needed for the whole application, like database connections or caches.
    
    :return: A dictionary with the following keys:
    :doc-author: Trelent
    """

    r = await redis.Redis(host=settings.redis_host, port=settings.redis_port, db=0, encoding='utf-8', decode_responses=True)
    await FastAPILimiter.init(r)


origins = ['http://localhost:3000']
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

@app.get("/")
def read_root():
    """
    The read_root function returns a dictionary with the key &quot;message&quot; and value &quot;Hello World&quot;.
    This is an example of how to use FastAPI's automatic documentation feature.
    
    
    :return: A dictionary with a single key-value pair
    :doc-author: Trelent
    """

    return {"message": "Hello World"}


if __name__ == '__main__':
    uvicorn.run(app, host='localhost', port=8000)