from fastapi import FastAPI

app = FastAPI(title="GEM BACKEND", version="1.0")

@app.get("/")
def read_root():
    return {"Olá mundo"}