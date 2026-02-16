# Colaberry Skill Gap Analyzer

A deterministic Python-based skill gap analyzer that compares job descriptions against candidate skills.

---

## 📌 Overview

The Skill Gap Analyzer extracts skills from text input and categorizes them into structured groups such as:

- Programming Languages
- Tools
- Databases
- Cloud
- Other Technical Skills

It is designed to be:

- Deterministic
- Testable
- Extensible
- Production-safe


## 🎓 Project Structure

```text
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

