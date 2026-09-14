# 24/7 Intelligent Code Reviewer

An automated, always-on code review system built entirely on Google Cloud Platform. Submit code, get instant multi-language bug reports, security analysis, architectural guidance, and a standardized 1–10 quality rating — grounded in historical review data.

**Built for Code Kitchen Season 01 — Track 01**

---

## 🎯 What It Does

- **Multi-language reviews** — Python, JavaScript, TypeScript, Go, Java
- **Bug detection** — logic errors, null pointers, race conditions
- **Security analysis** — SQL injection, XSS, hardcoded secrets
- **Architecture guidance** — best practices, design patterns
- **Quality rating** — standardized 1–10 score
- **Session history** — track developer growth over time
- **Historical learning** — RAG-grounded reviews from CSV rules

---

## 🏗️ Architecture

User → Firebase Auth → Cloud Run API → Pub/Sub → Cloud Run Worker
                                                      ↓
                                          ┌───────────┴───────────┐
                                          ↓                       ↓
                                    AST Parser              Gemini 2.5 Flash
                                    (symbolic)              (probabilistic)
                                          ↓                       ↓
                                          └───────────┬───────────┘
                                                      ↓
                                          ┌───────────┴───────────┐
                                          ↓                       ↓
                                      Firestore               BigQuery
                                   (session history)      (historical rules)
                                                                  ↓
                                                          Vertex AI Vector Search
                                                              (RAG retrieval)

---

## 🛠️ GCP Stack

| Service | Purpose |
|---|---|
| **Gemini 2.5 Flash** | Code reasoning, bug detection, review generation |
| **Firestore** | Session history, user profiles, growth tracking |
| **BigQuery** | Historical CSV rules, Developer Maturity Index |
| **Cloud Run** | API + worker deployment, autoscaling |
| **Pub/Sub** | Async job queueing |
| **Cloud Storage** | Temporary code artifacts |
| **Vertex AI Vector Search** | RAG embeddings for historical rules |
| **Firebase Auth** | User authentication |
| **Secret Manager** | API keys, tokens |
| **Cloud Build** | CI/CD pipeline |

---

## 🚀 Quick Start

```bash
git clone https://github.com/PreetiToppo/code_reviewer.git
cd code_reviewer
cp .env.example .env
pip install -r requirements.txt
uvicorn src.api.main:app --reload --port 8080
