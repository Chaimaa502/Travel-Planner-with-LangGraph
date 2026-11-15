"""FastAPI entrypoint for the travel planner."""

from fastapi import FastAPI

from travel_planner.models import TravelPlan, TripRequest
from travel_planner.workflow import create_travel_plan

app = FastAPI(title="AI Travel Planner", version="1.0.0")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/plan", response_model=TravelPlan)
def plan_trip(payload: TripRequest) -> TravelPlan:
    return create_travel_plan(payload.request)

