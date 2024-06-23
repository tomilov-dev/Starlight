from fastapi import FastAPI
from movies.app import router as movies_router
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200"],
    allow_credentials=True,
    allow_methods=["GET"],
    allow_headers=["X-Requested-With", "Content-Type", "Authorization"],
)

app.include_router(movies_router)
