from fastapi import APIRouter, status, HTTPException
from dishka.integrations.fastapi import FromDishka, DishkaRoute

router = APIRouter(prefix="/teams",
                   tags=["Teams"],
                   route_class=DishkaRoute)


@router.post("/", response_model=ProjectDTO
)

