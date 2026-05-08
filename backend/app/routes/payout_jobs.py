from fastapi import APIRouter
import app.db.database as database

router = APIRouter(prefix="/api/payout-jobs", tags=["payout-jobs"])

@router.get("/")
async def get_payout_jobs():
    """
    Queue monitoring: List all recent payout processing jobs.
    """
    if not database.payout_jobs_collection:
        return {"status": "error", "message": "Queue collection not initialized"}
        
    cursor = database.payout_jobs_collection.find({}).sort("created_at", -1)
    jobs = await cursor.to_list(length=100)
    
    for job in jobs:
        job["_id"] = str(job["_id"])
        job["user_id"] = str(job["user_id"])
        
    return {"status": "success", "data": jobs}
