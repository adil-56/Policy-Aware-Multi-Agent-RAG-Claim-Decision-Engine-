import asyncio
from fastapi import FastAPI
from backend.core.config import settings
from backend.api.routes import router

app = FastAPI(title=settings.PROJECT_NAME)

app.include_router(router, prefix=settings.API_V1_STR)

@app.on_event("startup")
async def startup_event():
    # Build the index in the background so it doesn't block startup or timeout the first request
    from backend.api.dependencies import get_retriever
    asyncio.create_task(asyncio.to_thread(get_retriever))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
