from fastapi import APIRouter
from fastapi.responses import HTMLResponse

from app.clients.service.logic import interpret_and_calculate
from app.clients.schema import PredictionInput

router = APIRouter(prefix="/clients", tags=["clients"])

@router.post("/predictions")
async def predict(data: PredictionInput):
    print("HERE")
    print(data.model_dump())
    return interpret_and_calculate(data.model_dump())


