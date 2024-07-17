from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


from movies.app import router as movies_router
from persons.app import router as persons_router
from users.app import router as users_router

app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200"],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["X-Requested-With", "Content-Type", "Authorization"],
)

app.include_router(movies_router)
app.include_router(persons_router)
app.include_router(users_router)
