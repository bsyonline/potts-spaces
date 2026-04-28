from fastapi import FastAPI

app = FastAPI(title="Potts Spaces")


@app.get("/hello")
async def hello():
    return {"message": "Hello, World!"}


@app.get("/health")
async def health():
    return {"status": "ok"}