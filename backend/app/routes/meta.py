import httpx
from fastapi import APIRouter
import app.db.database as database
from app.config import settings

router = APIRouter()

GOOGLE_API_KEY = settings.google_api_key


# -------------------------------
# PLATFORMS
# -------------------------------
@router.get("/platforms")
def get_platforms():
    return [
        "Blinkit",
        "Zepto",
        "Swiggy Instamart",
        "Dunzo",
        "Zomato",
        "Uber Eats"
    ]


# -------------------------------
# GET CITIES
# -------------------------------
@router.get("/cities")
async def get_cities():
    try:
        # ✅ FIX: safe DB access
        if database.meta_collection is None:
            return ["Delhi", "Mumbai", "Bangalore"]

        # Cache check
        cached = await database.meta_collection.find_one({"type": "cities"})
        if cached:
            return cached.get("data", [])

        # API key fallback
        if not GOOGLE_API_KEY:
            return ["Delhi", "Mumbai", "Bangalore"]

        url = "https://maps.googleapis.com/maps/api/place/autocomplete/json"
        params = {
            "input": "India",
            "types": "(cities)",
            "components": "country:in",
            "key": GOOGLE_API_KEY
        }

        async with httpx.AsyncClient(timeout=10.0) as client:
            res = await client.get(url, params=params)

        if res.status_code != 200:
            return ["Delhi", "Mumbai", "Bangalore"]

        data = res.json()

        cities = [
            p.get("structured_formatting", {}).get("main_text")
            for p in data.get("predictions", [])
        ]

        cities = [c for c in cities if c]

        # Cache
        if cities:
            await database.meta_collection.insert_one({
                "type": "cities",
                "data": cities
            })

        return cities or ["Delhi", "Mumbai", "Bangalore"]

    except Exception as e:
        print("CITIES ERROR:", e)
        return ["Delhi", "Mumbai", "Bangalore"]


# -------------------------------
# GET ZONES
# -------------------------------
@router.get("/zones/{city}")
async def get_zones(city: str):
    try:
        if database.meta_collection is None:
            return []

        # Cache check
        cached = await database.meta_collection.find_one({
            "type": "zones",
            "city": city
        })

        if cached:
            return cached.get("data", [])

        if not GOOGLE_API_KEY:
            return []

        url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
        params = {
            "query": f"areas in {city}",
            "key": GOOGLE_API_KEY
        }

        async with httpx.AsyncClient(timeout=10.0) as client:
            res = await client.get(url, params=params)

        if res.status_code != 200:
            return []

        data = res.json()

        zones = [
            r.get("name")
            for r in data.get("results", [])
            if r.get("name")
        ]

        # Cache
        if zones:
            await database.meta_collection.insert_one({
                "type": "zones",
                "city": city,
                "data": zones
            })

        return zones

    except Exception as e:
        print("ZONES ERROR:", e)
        return []


# -------------------------------
# CLEAR CACHE
# -------------------------------
@router.delete("/clear-cache")
async def clear_cache():
    try:
        if database.meta_collection:
            await database.meta_collection.delete_many({
                "type": {"$in": ["cities", "zones"]}
            })

        return {"message": "Cache cleared"}

    except Exception as e:
        print("CACHE ERROR:", e)
        return {"message": "Cache clear failed"}