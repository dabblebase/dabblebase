"""Exposes the main FastAPI server for the application."""

from fastapi import FastAPI
from .api import health, auth, course, profile, assignment, task
from .api.project import openapi_tags as project_openapi_tags
from .api.project import auth as project_auth

from fastapi.middleware.gzip import GZipMiddleware
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Dabblebase API",
    version="0.0.1",
    description="Dabblebase RESTful API",
    openapi_tags=[
        health.openapi_tags,
        task.openapi_tags,
        course.openapi_tags,
        profile.openapi_tags,
        assignment.openapi_tags,
        project_openapi_tags,
    ],
)

# Use GZip middleware for compressing HTML responses over the network
app.add_middleware(GZipMiddleware)

# Add CORS middleware so that credentials can be passed along via cookies
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

feature_apis = [health, task, auth, project_auth, course, profile, assignment]

for feature_api in feature_apis:
    app.include_router(feature_api.api)
