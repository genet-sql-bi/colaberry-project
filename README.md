# 🎓 Colaberry Skill Gap Analyzer

A deterministic Python-based skill gap analyzer that compares job descriptions (JD) against candidate skills and returns structured, categorized results.

---

## 🎯 Objective

Identify missing technical skills between a job description and a candidate profile, then generate a clear structured output for review, reporting, or integration.

---

## 📥 Supported Candidate Inputs

- **Manual Input** (user-entered skills)
- **Resume Text** (copy/paste resume content)
- **LinkedIn Text** (copy/paste profile content)

**Job Description Input:** JD text (copy/paste)

---

## 🏗 System Architecture

```text
                Candidate Inputs
     -----------------------------------
     Manual Input
     Resume Text
     LinkedIn Text
                     │
                     ▼
              Skill Extraction
                     │
                     ▼
JD Text ───► JD Extraction
                     │
                     ▼
                Gap Engine
                     │
                     ▼
             Structured Output


⚙ Core Gap Engine

The Gap Engine is implemented in:

src/skillgap_analyzer/analyzer.py

Responsibilities

Skill normalization

Category alignment

Missing skill detection

Structured result generation

Deterministic comparison logic

📂 Project Structure

colaberry-project/
│
├── src/skillgap_analyzer/
│   ├── analyzer.py
│   ├── cli.py
│   ├── schema.py
│   └── main.py
│
├── tests/
│
├── pyproject.toml
├── .gitignore
└── README.md

🧠 Processing Flow

Parse job description and extract required skills

Parse candidate input and extract candidate skills

Normalize skills (standard naming)

Map skills to categories (e.g., Languages, Tools, DB, Cloud)

Compute missing skills (JD - Candidate)

Return structured output

📊 Output

The analyzer produces a structured result including:

Required skills (from JD)

Candidate skills (from input)

Missing skills

Categorized breakdown

🔬 Design Principles

Deterministic (no randomness)

Testable

Extensible

Production-safe structure

Modular architecture

🏢 Enterprise Readiness

Designed to support future integration with:

ATS / HR pipelines

Resume parsing systems

Learning path recommendation engines

API-based deployment

🎓 Academic Value

Demonstrates:

Text processing and extraction

Rule-based gap comparison logic

Modular Python package design

Structured output modeling

Clean repository practices

🚀 Future Enhancements

Automated resume parsing module

LinkedIn API integration

Skill similarity scoring

Learning path recommendation engine

REST API interface