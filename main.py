from fastapi import FastAPI
import uvicorn
from api.crud.user_repository import router as user_router
from api.crud.product_repository import router as product_router
from api.crud.buy_product_repository import router as buy_product_router
from api.crud.cards_repository import router as cards_router
from api.crud.exchange_repository import router as exchange_router
from api.crud.rating_repository import router as rating_router
from api.crud.tasks_repository import router as tasks_router
from api.crud.coin_repository import router as coin_router
from fastapi.middleware.cors import CORSMiddleware
from api.crud.equipment_repository import router as equipment_router

app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(user_router)
app.include_router(product_router)
app.include_router(buy_product_router)
app.include_router(cards_router)
app.include_router(exchange_router)
app.include_router(rating_router)
app.include_router(tasks_router)
app.include_router(coin_router)
app.include_router(equipment_router)


if __name__ == "__main__":
    uvicorn.run("main:app") 