# 🎓 Colaberry Skill Gap Analyzer

A deterministic Python-based system that analyzes skill gaps between job descriptions and candidate skill profiles.

---

## 📌 Executive Summary

The **Colaberry Skill Gap Analyzer** extracts, categorizes, and compares technical skills from multiple input sources to identify missing competencies between:

- Job Descriptions (JD)
- Candidate Profiles (Manual Input, Resume Text, LinkedIn Text)

The system is designed to be:

- ✅ Deterministic  
- ✅ Testable  
- ✅ Modular  
- ✅ Extensible  
- ✅ Production-safe  

---

# 🏗 System Architecture



```
                    ┌────────────────────┐
Manual Input  ──────┐                    │
Resume Text   ──────┼──► Skill Extraction ├──►
LinkedIn Text ──────┘                    │
                    └────────────────────┘
                                 │
                                 ▼
                        ┌────────────────┐
JD Text ───────────────►│ JD Extraction  │
                        └────────────────┘
                                 │
                                 ▼
                        ┌────────────────┐
                        │ Gap Engine     │
                        │ (analyzer.py)  │
                        └────────────────┘
                                 │
                                 ▼
                        Structured Output
```



# 🎯 Features

- Extract structured skills from:
  - Job descriptions
  - Manual skill input
  - Resume text
  - LinkedIn profile text
- Categorize skills into:
  - Programming Languages
  - Tools
  - Databases
  - Cloud
  - Other Technical Skills
- Identify:
  - Missing skills
  - Matching skills
  - Skill gaps
- Deterministic processing (no randomness)
- Fully testable with unit tests

---

# 📁 Project Structure

```
colaberry-project/
│
├── src/skillgap_analyzer/
│   ├── analyzer.py        # Core gap analysis engine
│   ├── cli.py             # Command-line interface
│   ├── schema.py          # Skill schema definitions
│   └── main.py            # Entry point
│
├── tests/                 # Unit tests
│
├── pyproject.toml         # Project configuration
├── .gitignore             # Git ignore rules
└── README.md              # Documentation
```

---

# ⚙️ Installation

Create a virtual environment:

```bash
python -m venv venv
venv\Scripts\activate   # Windows
# or
source venv/bin/activate  # Mac/Linux
```

Install the project locally:

```bash
pip install -e .
```

---

# 🚀 Usage

Run via CLI:

```bash
python -m skillgap_analyzer.main
```

Or use programmatically:

```python
from skillgap_analyzer.analyzer import SkillGapAnalyzer

jd_text = "We need Python, AWS, SQL"
candidate_skills = ["Python", "SQL"]

analyzer = SkillGapAnalyzer()
result = analyzer.analyze(jd_text, candidate_skills)

print(result)
```

---

# 🧪 Testing

Run unit tests:

```bash
pytest
```

Testing principles:

- Deterministic outputs
- No external API dependency
- Reproducible results
- Structured validation

---

# 🎓 Academic Context

This project demonstrates:

- Structured schema modeling
- Deterministic text categorization
- Skill taxonomy design
- Clean architecture separation
- Unit-test-driven validation
- Reproducible engineering practices

It is suitable for academic evaluation in:

- Software Engineering
- Data Engineering
- Applied NLP (Deterministic approach)
- Systems Design

---

# 🏢 Enterprise Context

This system can serve as a foundation for:

- Workforce skill gap analysis
- Recruitment intelligence systems
- Resume screening automation
- Learning path recommendation engines
- Talent analytics dashboards

Designed for:

- HR platforms
- Internal talent mobility systems
- Enterprise recruitment pipelines

---

# 🔮 Future Enhancements

- NLP-based skill extraction
- Learning path auto-generation
- REST API integration (FastAPI)
- Database integration
- Cloud deployment (AWS/Azure)
- Analytics dashboard

---

# 📜 License

For academic and demonstration purposes.

---

# 👨‍💻 Genet

Colaberry Skill Gap Analyzer Project  
Python | Deterministic Systems | Structured Engineering

