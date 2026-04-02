"""FastAPI application — thin routing layer only. No business logic here."""

from typing import Any, Optional

from fastapi import Body, FastAPI, File, Form, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from skillgap_analyzer.analyzer import extract_text_from_pdf_bytes
from skillgap_analyzer.service import analyze_skill_gap

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["POST"],
    allow_headers=["Content-Type"],
)


@app.post("/analyze")
def analyze(input_data: dict[str, Any] = Body(...)) -> dict[str, Any]:
    """Analyze skill gaps and generate curriculum recommendations.
    
    Returns a dict with:
      - categories: list of skill gaps with categorization and priority
      - curriculum: structured learning paths derived from gaps
    """
    return analyze_skill_gap(input_data)


@app.post("/upload-analyze")
async def upload_analyze(
    jd_text: str = Form(...),
    skills: str = Form(""),
    resume_file: Optional[UploadFile] = File(None),
    linkedin_file: Optional[UploadFile] = File(None),
) -> dict[str, Any]:
    """Analyze skill gaps from uploaded PDFs and generate curriculum recommendations.
    
    Returns a dict with:
      - categories: list of skill gaps with categorization and priority
      - curriculum: structured learning paths derived from gaps
    """
    input_data: dict[str, Any] = {
        "jd_text": jd_text,
        "skills": [s.strip() for s in skills.split(",") if s.strip()],
    }
    if resume_file and resume_file.filename:
        resume_bytes = await resume_file.read()
        input_data["resume_text"] = extract_text_from_pdf_bytes(resume_bytes)
    if linkedin_file and linkedin_file.filename:
        linkedin_bytes = await linkedin_file.read()
        input_data["linkedin_text"] = extract_text_from_pdf_bytes(linkedin_bytes)
    return analyze_skill_gap(input_data)
