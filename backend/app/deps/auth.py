from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from app.db.database import get_users_collection
from app.utils.security import decode_access_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


# -------------------------------
# GET CURRENT USER (FIXED 🔥)
# -------------------------------
async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired token",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        token_data = decode_access_token(token)

        # ✅ Support both dict & object
        if isinstance(token_data, dict):
            pan = token_data.get("pan")
        else:
            pan = getattr(token_data, "pan", None)

        if not pan:
            raise credentials_exception

    except Exception as e:
        raise credentials_exception

    # ✅ SAFE DB ACCESS
    try:
        users_collection = get_users_collection()
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database not initialized"
        )

    user = await users_collection.find_one({"pan": pan})

    if not user:
        raise credentials_exception

    return user


# -------------------------------
# ADMIN CHECK (SAFE)
# -------------------------------
async def get_current_admin(user: dict = Depends(get_current_user)):
    if user.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required"
        )
    return user