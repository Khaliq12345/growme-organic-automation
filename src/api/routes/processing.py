from typing import List
from fastapi import APIRouter, HTTPException
from src.services.scraping_service import run

router = APIRouter(prefix="", responses={404: {"description": "Not found"}})


@router.post("/start-scraping")
def get_lead_route(domains: List[str], headless: bool = True):
    try:
        result = run(headless, domains)  # ["agola.com", "ikilo.fr", "dorsal.bj"]
        return {
            "details": f"Output Successfully Generated : {result}"
            if result
            else "Processing Error"
        }
    except Exception as e:
        raise HTTPException(detail=str(e), status_code=500)
