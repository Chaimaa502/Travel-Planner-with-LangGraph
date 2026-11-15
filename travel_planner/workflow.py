"""A deterministic multi-agent travel planning workflow.

The workflow deliberately does not pretend to have live inventory.  Flight and
hotel entries are clearly labelled suggestions until real search tools are
configured.
"""

import re
from typing import TypedDict

from langchain_core.prompts import PromptTemplate
from langgraph.graph import END, START, StateGraph

from .models import FlightSuggestion, HotelSuggestion, ItineraryDay, TravelPlan


class PlannerState(TypedDict, total=False):
    request: str
    destination: str
    origin: str
    trip_length_days: int
    flights: list[FlightSuggestion]
    hotels: list[HotelSuggestion]
    itinerary: list[ItineraryDay]
    plan: TravelPlan


_DESTINATION = re.compile(r"\b(?:to|in|visit)\s+([A-Z][A-Za-z]+(?:\s+[A-Z][A-Za-z]+)*)")
_ORIGIN = re.compile(r"\bfrom\s+([A-Z][A-Za-z]+(?:\s+[A-Z][A-Za-z]+)*)")
_DURATION = re.compile(r"\b(\d+)\s*(?:day|days|night|nights)\b", re.IGNORECASE)

# Prompts are kept as LangChain objects so an LLM-backed node can be added
# without changing the graph's public contract.
FLIGHT_PROMPT = PromptTemplate.from_template(
    "Suggest practical flight options for a trip from {origin} to {destination}."
)
HOTEL_PROMPT = PromptTemplate.from_template(
    "Suggest hotel areas and accommodation styles in {destination}."
)


def _extract_location(pattern: re.Pattern[str], text: str, default: str) -> str:
    match = pattern.search(text)
    return match.group(1).strip(" .,") if match else default


def parse_request(state: PlannerState) -> PlannerState:
    text = state["request"]
    days_match = _DURATION.search(text)
    days = int(days_match.group(1)) if days_match else 3
    return {
        "destination": _extract_location(_DESTINATION, text, "your destination"),
        "origin": _extract_location(_ORIGIN, text, "your departure city"),
        "trip_length_days": max(1, min(days, 30)),
    }


def suggest_flights(state: PlannerState) -> PlannerState:
    destination = state["destination"]
    origin = state["origin"]
    return {
        "flights": [
            FlightSuggestion(
                airline="Compare major and regional carriers",
                route=f"{origin} → {destination}",
                recommendation="Check flexible dates and include one carry-on in the fare comparison.",
            )
        ]
    }


def suggest_hotels(state: PlannerState) -> PlannerState:
    destination = state["destination"]
    return {
        "hotels": [
            HotelSuggestion(
                name=f"Central {destination} stay",
                area="Central district",
                recommendation="Choose a well-reviewed property near public transport; verify current rates and availability.",
            ),
            HotelSuggestion(
                name=f"Local {destination} neighborhood stay",
                area="Residential neighborhood",
                recommendation="Consider a guesthouse or apartment for a quieter, more local experience.",
            ),
        ]
    }


def build_itinerary(state: PlannerState) -> PlannerState:
    destination = state["destination"]
    days = state["trip_length_days"]
    itinerary = [
        ItineraryDay(day=1, activities=[f"Arrive in {destination}", "Settle in and take an orientation walk"]),
    ]
    for day in range(2, days + 1):
        itinerary.append(
            ItineraryDay(
                day=day,
                activities=[
                    f"Explore a signature area of {destination}",
                    "Leave time for a local meal and an unscheduled discovery",
                ],
            )
        )
    return {"itinerary": itinerary}


def assemble_plan(state: PlannerState) -> PlannerState:
    return {
        "plan": TravelPlan(
            destination=state["destination"],
            origin=state["origin"],
            trip_length_days=state["trip_length_days"],
            flights=state["flights"],
            hotels=state["hotels"],
            itinerary=state["itinerary"],
        )
    }


def build_workflow():
    """Compile the planner's parse, specialist, and assembly agents."""

    graph = StateGraph(PlannerState)
    graph.add_node("parse_request", parse_request)
    graph.add_node("suggest_flights", suggest_flights)
    graph.add_node("suggest_hotels", suggest_hotels)
    graph.add_node("build_itinerary", build_itinerary)
    graph.add_node("assemble_plan", assemble_plan)
    graph.add_edge(START, "parse_request")
    graph.add_edge("parse_request", "suggest_flights")
    graph.add_edge("parse_request", "suggest_hotels")
    graph.add_edge("parse_request", "build_itinerary")
    graph.add_edge("suggest_flights", "assemble_plan")
    graph.add_edge("suggest_hotels", "assemble_plan")
    graph.add_edge("build_itinerary", "assemble_plan")
    graph.add_edge("assemble_plan", END)
    return graph.compile()


planner = build_workflow()


def create_travel_plan(request: str) -> TravelPlan:
    """Run the graph for a natural-language request."""

    result = planner.invoke({"request": request})
    return result["plan"]

