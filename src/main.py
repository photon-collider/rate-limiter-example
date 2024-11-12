from fastapi import FastAPI, Request, Response, HTTPException, status
from redis import Redis
import os
from time import time
import math

# Number of tokens to add to the bucket per second
BUCKET_REPLENISH_RATE = int(os.getenv("BUCKET_REPLENISH_RATE"))

# Max number of tokens the bucket can carry
BUCKET_CAPACITY = int(os.getenv("BUCKET_CAPACITY"))

TOKENS_PER_REQUEST = int(os.getenv("TOKENS_PER_REQUEST"))


def calculate_retry_seconds(current_tokens, tokens_needed, replenish_rate):
    tokens_to_replenish = tokens_needed - current_tokens
    if tokens_to_replenish <= 0:
        return 0

    seconds = math.ceil(tokens_to_replenish / replenish_rate)
    return seconds


def get_script_hash(redis_client: Redis, rel_path_to_script: str):
    main_dir = os.path.dirname(os.path.abspath(__file__))
    script_path = os.path.join(main_dir, rel_path_to_script)

    with open(script_path, "r") as f:
        script_content = f.read()

    return redis_client.script_load(script_content)


redis_client = Redis(host=os.getenv("REDIS_HOST"), port=os.getenv("REDIS_PORT"))
script_hash = get_script_hash(redis_client, "./request_rate_limiter.lua")

app = FastAPI()


@app.middleware("http")
async def check_request(request: Request, call_next):
    client_ip = request.client.host
    prefix = "request_rate_limiter." + client_ip

    # Redis keys for token bucket
    keys = [prefix + ".tokens", prefix + ".timestamp"]
    args = [BUCKET_REPLENISH_RATE, BUCKET_CAPACITY, time(), TOKENS_PER_REQUEST]
    allowed, new_tokens = redis_client.evalsha(script_hash, len(keys), *keys, *args)

    retry_after = math.ceil(1 / BUCKET_REPLENISH_RATE)

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
