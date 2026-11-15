"""Public request and response models for the travel planner."""

from pydantic import BaseModel, Field, field_validator


class TripRequest(BaseModel):
    """A natural-language trip request."""

    request: str = Field(..., min_length=10, max_length=2000)

    @field_validator("request")
    @classmethod
    def request_must_not_be_blank(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("request must not be blank")
        return value.strip()


class FlightSuggestion(BaseModel):
    airline: str
    route: str
    recommendation: str


class HotelSuggestion(BaseModel):
    name: str
    area: str
    recommendation: str


class ItineraryDay(BaseModel):
    day: int
    activities: list[str]


class TravelPlan(BaseModel):
    destination: str
    origin: str
    trip_length_days: int
    flights: list[FlightSuggestion]
    hotels: list[HotelSuggestion]
    itinerary: list[ItineraryDay]

