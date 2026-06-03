import sys
import os
import asyncio
from datetime import datetime

# Adjust sys.path to run from root backend folder
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.config import settings
from motor.motor_asyncio import AsyncIOMotorClient

async def run_migration():
    print("[INFO] Starting GigSurance Schema Migration V2...")
    
    mongo_uri = settings.mongo_uri
    db_name = settings.db_name
    
    if not mongo_uri:
        print("[ERROR] MONGO_URI not found in configuration")
        return
        
    print(f"Connecting to database: {db_name}")
    client = AsyncIOMotorClient(mongo_uri)
    db = client[db_name]
    
    # 1. Update users collection
    print("Updating 'users' collection...")
    users_coll = db["users"]
    
    # Add default kyc_status if it doesn't exist
    res_users = await users_coll.update_many(
        {"kyc_status": {"$exists": False}},
        {"$set": {
            "kyc_status": "uninitiated",
            "kyc_verified_at": None,
            "kyc_document_type": None,
            "kyc_document_ref": None
        }}
    )
    print(f"-> Updated {res_users.modified_count} user documents for KYC fields.")

    # Add default role if it doesn't exist
    res_roles = await users_coll.update_many(
        {"role": {"$exists": False}},
        {"$set": {"role": "user"}}
    )
    print(f"-> Updated {res_roles.modified_count} user documents for default role.")

    # 2. Update policies collection
    # Transition policies of unverified users to pending_kyc
    print("Updating 'policies' collection...")
    policies_coll = db["policies"]
    
    # Get all users with kyc_status != "verified"
    unverified_users = await users_coll.find(
        {"kyc_status": {"$ne": "verified"}}
    ).to_list(length=None)
    
    unverified_user_ids = [str(u["_id"]) for u in unverified_users]
    
    res_policies = await policies_coll.update_many(
        {
            "user_id": {"$in": unverified_user_ids},
            "status": "active"
        },
        {"$set": {"status": "pending_kyc", "updated_at": datetime.utcnow()}}
    )
    print(f"-> Transitioned {res_policies.modified_count} active policies of unverified users to 'pending_kyc'.")
    
    # 3. Create Indexes
    print("Creating database indexes...")
    try:
        await users_coll.create_index([("email", 1)], unique=True)
    except Exception as e:
        print(f"Index check email failed (already exists or duplicates exist): {e}")

    try:
        await users_coll.create_index([("pan", 1)], unique=True)
    except Exception as e:
        print(f"Index check pan failed: {e}")

    await users_coll.create_index([("kyc_status", 1)])
    await users_coll.create_index([("role", 1)])
    
    await db["kyc_logs"].create_index([("user_id", 1)])
    await db["kyc_logs"].create_index([("user_id", 1), ("created_at", -1)])
    
    print("[SUCCESS] Migration completed successfully!")
    client.close()

if __name__ == "__main__":
    asyncio.run(run_migration())
