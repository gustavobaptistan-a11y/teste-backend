from fastapi import APIRouter

router = APIRouter()

@router.get("/")
def home():
    return {
        "message": "Bem-vindo a Lifeline One"
    }