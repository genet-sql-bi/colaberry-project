"""FastAPI application — thin routing layer only. No business logic here."""

from typing import Any

from fastapi import Body, FastAPI

from skillgap_analyzer.service import analyze_skill_gap

app = FastAPI()


@app.post("/analyze")
def analyze(input_data: dict[str, Any] = Body(...)) -> dict[str, Any]:
    return analyze_skill_gap(input_data)
