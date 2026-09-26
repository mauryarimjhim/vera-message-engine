from typing import Dict
from app.categories.base import BaseCategoryHandler
from app.categories.dentists import DentistsCategoryHandler
from app.categories.salons import SalonsCategoryHandler
from app.categories.restaurants import RestaurantsCategoryHandler
from app.categories.gyms import GymsCategoryHandler
from app.categories.pharmacies import PharmaciesCategoryHandler

_HANDLERS: Dict[str, BaseCategoryHandler] = {
    "dentists": DentistsCategoryHandler(),
    "salons": SalonsCategoryHandler(),
    "restaurants": RestaurantsCategoryHandler(),
    "gyms": GymsCategoryHandler(),
    "pharmacies": PharmaciesCategoryHandler(),
}

def get_category_handler(slug: str) -> BaseCategoryHandler:
    return _HANDLERS.get(slug, DentistsCategoryHandler())
