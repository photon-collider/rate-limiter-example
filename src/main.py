from fastapi import FastAPI, Request, Response, HTTPException, status
from contextlib import asynccontextmanager

# from redis import Redis
from redis.asyncio import Redis
import os
from time import time
import math

# Number of tokens to add to the bucket per second
BUCKET_REPLENISH_RATE = 2

# Max number of tokens the bucket can carry
BUCKET_CAPACITY = 10

# Number of tokens needed to make a request
TOKENS_PER_REQUEST = 1


async def get_script_hash(redis_client: Redis, rel_path_to_script: str):
    main_dir = os.path.dirname(os.path.abspath(__file__))
    script_path = os.path.join(main_dir, rel_path_to_script)

    with open(script_path, "r") as f:
        script_content = f.read()

    return await redis_client.script_load(script_content)


redis_client = None
script_hash = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global redis_client, script_hash
    redis_client = Redis(host=os.getenv("REDIS_HOST"), port=os.getenv("REDIS_PORT"))
    script_hash = await get_script_hash(redis_client, "./request_rate_limiter.lua")

    yield
    await redis_client.close()


app = FastAPI(lifespan=lifespan)


@app.middleware("http")
async def check_request(request: Request, call_next):
    client_ip = request.client.host
    prefix = "request_rate_limiter." + client_ip

    # Redis keys for token bucket
    keys = [prefix + ".tokens", prefix + ".timestamp"]
    args = [BUCKET_REPLENISH_RATE, BUCKET_CAPACITY, time(), TOKENS_PER_REQUEST]
    allowed, new_tokens = await redis_client.evalsha(
        script_hash, len(keys), *keys, *args
    )

    retry_after = math.ceil(TOKENS_PER_REQUEST / BUCKET_REPLENISH_RATE)

    if allowed:
        response = await call_next(request)
        response.headers["X-RateLimit-Remaining"] = str(new_tokens)
        response.headers["Retry-After"] = str(retry_after)
        return response
    else:
        return Response(
            content="Too many requests",
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            media_type="text/plain",
            headers={"X-RateLimit-Remaining": "0", "Retry-After": str(retry_after)},
        )


@app.get("/api/example")
def get_example():
    return {"message": "This is a rate limited endpoint"}
