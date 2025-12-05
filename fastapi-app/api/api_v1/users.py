from fastapi import APIRouter

router = APIRouter()

 
# Список пользователей
@router.get("/")
async def list():
    pass


# Просмотр собственного профиля
@router.get("/me")
async def get_my_profile():
    pass


# Обновление информации о себе
@router.put("/me")
async def update_my_profile():
    pass


# Просмотреть список собственных матчей
@router.get("/me/matches")
async def get_my_matches():
    pass


# Просмотреть профиль пользователя
@router.get("/{id}")
async def get_by_id(id: int):
    pass


# Просмотреть список матчей пользователя
@router.get("/{id}/matches")
async def get_user_matches(id: int):
    pass
