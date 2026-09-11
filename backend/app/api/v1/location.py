from typing import List
from fastapi import APIRouter, Query
from app.schemas.weather import LocationInfo
from app.core.security import sanitize_input_text

router = APIRouter(prefix="/location", tags=["Location Resolution"])


@APIRouter.get(router, "/search", response_model=List[LocationInfo])
async def search_locations(
    query: str = Query(..., min_length=1, max_length=100)
):
    """
    Resolves city and geographical location search queries.
    """
    clean_q = sanitize_input_text(query).lower()
    
    known_locations = [
        LocationInfo(name="Tokyo, Japan", latitude=35.6762, longitude=139.6503, country="Japan", timezone="Asia/Tokyo"),
        LocationInfo(name="London, UK", latitude=51.5074, longitude=-0.1278, country="United Kingdom", timezone="Europe/London"),
        LocationInfo(name="New York, USA", latitude=40.7128, longitude=-74.0060, country="United States", timezone="America/New_York"),
        LocationInfo(name="Denver, USA", latitude=39.7392, longitude=-104.9903, country="United States", timezone="America/Denver"),
        LocationInfo(name="Paris, France", latitude=48.8566, longitude=2.3522, country="France", timezone="Europe/Paris"),
        LocationInfo(name="Mumbai, India", latitude=19.0760, longitude=72.8777, country="India", timezone="Asia/Kolkata"),
    ]

    matches = [loc for loc in known_locations if clean_q in loc.name.lower() or clean_q in (loc.country or "").lower()]
    if not matches:
        matches = [LocationInfo(name=f"Location '{clean_q.capitalize()}'", latitude=40.0, longitude=-75.0, country="Global")]
        
    return matches
