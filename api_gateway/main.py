from fastapi import FastAPI
from routers import router


application = FastAPI()

application.include_router(router)




