from fastapi import FastAPI

from app.api.v1.router import router

app = FastAPI()

app.include_router(router=router)

@app.get("/health")
def health():
    return {"status" : "OK"}

