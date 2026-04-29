from fastapi import Request
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError


async def integrity_error_handler(request: Request, exc: IntegrityError) -> JSONResponse:
    orig = str(exc.orig).lower() if exc.orig else ""
    if "unique constraint" in orig:
        message = "This value already exists and must be unique."
    elif "foreign key constraint" in orig:
        message = "Referenced record does not exist."
    else:
        message = "A database integrity error occurred."
    return JSONResponse(status_code=400, content={"detail": message})
