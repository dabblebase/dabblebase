"""Exposes the main FastAPI server for the application."""

from fastapi import FastAPI
from .api import health
from fastapi.middleware.gzip import GZipMiddleware

app = FastAPI(
    title="Tinkerbase API",
    version="0.0.1",
    description="Tinkerbase RESTful API",
    openapi_tags=[health.openapi_tags],
)

# Use GZip middleware for compressing HTML responses over the network
app.add_middleware(GZipMiddleware)

feature_apis = [health]

for feature_api in feature_apis:
    app.include_router(feature_api.api)
