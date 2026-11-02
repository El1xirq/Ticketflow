from fastapi import FastAPI

from app.api.v1.router import router
from app.core.exceptions.handlers import (
    RequestValidationError,
    validation_exception_handler,
    app_exception_handler,
    global_exception_handler,
)
from app.core.exceptions.base import AppException

app = FastAPI()

app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(AppException, app_exception_handler)
app.add_exception_handler(Exception, global_exception_handler)


app.include_router(router)