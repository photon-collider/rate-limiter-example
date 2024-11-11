from fastapi import FastAPI, Request

app = FastAPI()


@app.middleware("http")
async def check_request(request: Request, call_next):
    pass


@app.get("/api/example")
def get_example():
    return {"message": "This is a rate limited endpoint"}
