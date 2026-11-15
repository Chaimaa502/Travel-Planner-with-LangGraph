# Travel Planner with LangGraph

An AI travel planner that turns a natural-language trip request into flight
suggestions, hotel ideas, and a day-by-day itinerary. The specialist nodes are
organized as a LangGraph workflow and exposed through FastAPI.

## Run locally

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload
```

Create a plan:

```bash
curl -X POST http://localhost:8000/plan \
  -H 'content-type: application/json' \
  -d '{"request":"Plan a 5 day trip from New York to Lisbon"}'
```

`/health` is available for service checks. Suggestions are intentionally
labelled as recommendations rather than live inventory; connect authenticated
flight and hotel search tools to replace them with real-time availability.

Run the focused tests with `python -m unittest discover`.
