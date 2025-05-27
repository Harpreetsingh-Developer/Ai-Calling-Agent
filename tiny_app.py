#!/usr/bin/env python3
"""
Tiny test app to verify FastAPI and Uvicorn are working.
"""

from fastapi import FastAPI
import uvicorn

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello World"}

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000) 