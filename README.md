# TransformIQ — Enterprise Transformation Intelligence Platform

TransformIQ is an **Enterprise Transformation Intelligence Platform** designed to model, evaluate, score, and guide large-scale organisational AI transformations.

Built on an authoritative, deterministic enterprise fact base in **PostgreSQL + pgvector**, TransformIQ combines multi-hop graph traversal, weighted multi-factor scoring, evidence-grounded Retrieval-Augmented Generation (RAG), and intent-routed AI analysis into a unified C-suite executive dashboard.

---

## 1. Project Overview

Modern enterprise AI adoption fails when organisations treat AI initiatives as isolated technology deployments rather than systemic transformation across strategies, processes, workforce roles, skills, governance, and technical dependencies.

TransformIQ provides C-suite leaders with a **deterministic source of truth** to prioritize AI use cases, map workforce reskilling priorities, enforce AI governance, and evaluate unseen natural language transformation scenarios.

```
                            EXECUTIVE USER / C-SUITE INTERFACE
                                            │
                                            ▼
                    Executive AI Analyst (Intent Classification Router)
                                            │
           +--------------------------------+--------------------------------+
           │                                                                 │
           ▼                                                                 ▼
[Deterministic Query Routing]                                    [Natural Language Scenario]
  ├── Priority Ranking Engine                                       (e.g., "Warehouse Slotting")
  ├── Process Intelligence Engine                                            │
  ├── Role Automation/Augmentation Engine                                    ▼
  ├── Skill Priority & Gap Engine                                 Phase 4A LLM Extraction
  ├── Governance Risk Portfolio Engine                                       │
  └── Dependency Traversal Engine                                            ▼
           │                                                    pgvector Semantic Match
           │                                                                 │
           +--------------------------------+--------------------------------+
                                            │
                                            ▼
                     Phase 3 Deterministic Intelligence Engine
                  (100% Authoritative Priority Score: 0.0 - 100.0)
                                            │
                                            ▼
                     Phase 4B RAG Evidence & Citation Engine
                     (Verified Chunks from pgvector Index)
                                            │
                                            ▼
                        Interactive Dashboard & Graph Interface
                 (Vite + React + TypeScript + Vanilla CSS + React Flow)
```

---

## 2. Business Problem

Enterprise leaders struggle to answer foundational transformation questions:
- **Which AI initiatives should we fund first?** (Avoiding subjective pitch-deck scoring)
- **Which processes yield the greatest business value?** (Mapping value chain impact)
- **How will AI impact our workforce?** (Distinguishing automation from human augmentation)
- **What skills must we build?** (Pinpointing workforce reskilling priorities)
- **What compliance risks are we taking?** (Enforcing human oversight and explainability audit controls)
- **What technical dependencies block execution?** (Preventing circular dependency deadlocks)

TransformIQ addresses this problem by separating **authoritative calculation** (handled 100% deterministically by PostgreSQL and backend python engines) from **narrative synthesis** (handled by LLMs).

---

## 3. What TransformIQ Does

TransformIQ models an enterprise as a fully connected propagation chain:
$$\text{Strategy} \rightarrow \text{Value Chain} \rightarrow \text{Process} \rightarrow \text{Activity} \rightarrow \text{AI Opportunity} \rightarrow \text{Role} \rightarrow \text{Skill} \rightarrow \text{Governance} \rightarrow \text{Initiative} \rightarrow \text{Dependency}$$

### Core Platform Capabilities:
1. **Deterministic Priority Scoring**: Evaluates transformation scenarios across 7 weighted factors to output authoritative scores ($0.0 - 100.0$).
2. **Impact Propagation Engine**: Executes 2-hop graph traversals to discover all affected processes, activities, roles, skills, and governance records.
3. **Multi-Hop Dependency Engine**: Traverses polymorphic directed graph edges with Depth-First Search (DFS) cycle detection to highlight prerequisite blockers.
4. **pgvector Semantic Enterprise Search**: Dynamically matches natural language scenario prompts to existing enterprise processes via 384-dimensional dense vector embeddings.
5. **Evidence-Grounded RAG Engine**: Retrieves external research evidence from `pgvector` with strict URL allowlists and dynamic similarity thresholding.
6. **Executive AI Analyst**: Routes C-suite questions to backend deterministic engines and generates evidence-grounded briefings with complete audit transparency.

---

## 4. NovaMart Synthetic Enterprise Dataset

TransformIQ includes a comprehensive synthetic retail enterprise dataset (**NovaMart**):
- **Industry**: Omnichannel Retail
- **Empirically Verified Seeded Domain Entities**:
  - **1 Organisation**: NovaMart
  - **3 Strategies**: Become an AI-enabled retailer, Optimize omnichannel supply chain, Enhance customer hyper-personalization
  - **4 Value Chains**: Supply Chain & Merchandising, Store & Digital Operations, Customer Experience & Marketing, Corporate & Shared Services
  - **10 Processes**: Demand Forecasting, Supplier Order Fulfillment, Store Inventory Management, Assortment Planning, Price Optimization, Checkout & Payment, Customer Support, Personalized Promotions, Workforce Scheduling, Financial Reconciliation
  - **24 Activities**: Operational, review, manual, automated, and decision activities across processes
  - **8 AI Opportunities**: AI-Powered Demand Forecasting, Dynamic Markdown, Automated Supplier Replenishment, Smart Assortment Engine, Customer Support Copilot, Visual Planogram Inspector, Predictive Shrink Detection, Real-Time Personalization Engine
  - **8 Roles**: Demand Planner, Supply Chain Analyst, Category Manager, Store Manager, Marketing Specialist, Customer Support Lead, Pricing Analyst, Inventory Controller
  - **10 Skills**: Demand Forecasting, Supply Chain Analytics, Data Analysis, Inventory Optimization, AI Oversight, Customer Service Management, Price Modeling, Omnichannel Operations, Prompt Engineering, SQL & Data Querying
  - **6 Governance Audit Records**: Privacy, explainability, human oversight, bias & fairness, and model risk records
  - **3 Initiatives**: Enterprise AI Supply Chain Modernization, Next-Gen Omnichannel Customer Experience, Smart Store Operations & Computer Vision
  - **3 Dependencies**: Directed prerequisite and impact relationships across initiatives, opportunities, and processes
  - **77 Transformation Analyses**: Historical execution and audit logs generated during scenario evaluations and automated testing *(Note: Transformation Analyses are historical execution/audit records and are kept separate from the count of current AI Opportunities)*

---

## 5. Key Executive Questions Supported

The Executive AI Analyst intent router maps natural language prompts directly to backend deterministic services:

| Executive Question | Intent Enum | Deterministic Backend Service | Output Data |
| :--- | :--- | :--- | :--- |
| *"What should we transform first?"* | `PRIORITY_RANKING` | `PriorityIntelligenceService` | Ranked priority matrix sorted by 7-factor score. |
| *"Which processes have the greatest AI opportunity?"* | `PROCESS_INTELLIGENCE` | `ProcessIntelligenceService` | Process deep-dive, activities, and linked opportunities. |
| *"Which roles will change most?"* | `ROLE_IMPACT` | `RoleIntelligenceService` | Potential automation vs augmentation activity breakdown. |
| *"What skills should we invest in?"* | `SKILL_INVESTMENT` | `SkillIntelligenceService` | Skill demand heatmap and reskilling focus areas. |
| *"What are our highest AI governance risks?"* | `GOVERNANCE_RISK` | `GovernanceIntelligenceService` | Risk portfolio, high-risk count, human oversight mandates. |
| *"What dependencies could prevent transformation?"* | `DEPENDENCY_BLOCKERS` | `DependencyIntelligenceService` | Multi-hop graph nodes, edges, and cycle detection. |

---

## 6. Architecture

TransformIQ enforces strict separation between the persistent enterprise state, deterministic intelligence engines, vector retrieval services, and the presentation layer:

```
[ Frontend: Vite + React + TypeScript + Vanilla CSS ]
                         │  (REST API / HTTP JSON)
                         ▼
[ FastAPI App Router: /api/v1/intelligence, /api/v1/analysis, /api/v1/scenarios ]
                         │
        +----------------+----------------+
        │                                 │
        ▼                                 ▼
[ Intelligence Services ]        [ AI Layer: Providers & Services ]
  ├── PriorityService              ├── ScenarioExtractionService
  ├── ProcessService               ├── ExecutiveExplanationService
  ├── RoleService                  └── Provider Abstraction (Ollama / MockLLM)
  ├── SkillService                        │
  ├── GovernanceService                   ▼
  └── DependencyService          [ Vector & RAG Layer ]
        │                          ├── EmbeddingProvider (local 384-dim dense vectors)
        ▼                          ├── EnterpriseSemanticRetriever (pgvector)
[ Deterministic Engines ]         ├── ResearchRetriever (pgvector HNSW)
  ├── ScoringEngine (7-factor)     └── ResearchIngestionService (URL Allowlist)
  ├── ImpactEngine (2-hop DFS)            │
  └── DependencyEngine (Cycles)           │
        │                                 │
        +----------------+----------------+
                         │
                         ▼
[ Data Layer: Async SQLAlchemy 2.0 ORM ]
                         │
                         ▼
[ Database: PostgreSQL 16 + pgvector (ankane/pgvector:v0.5.1) ]
  ├── Domain Tables (organisations, processes, roles, skills, etc.)
  ├── HNSW Index: idx_enterprise_entity_embeddings (384-dim)
  └── HNSW Index: idx_document_chunks_embedding (384-dim)
```

---

## 7. Enterprise Data Model

Defined using SQLAlchemy 2.0 Async ORM with UUID primary keys and timestamp mixins:

1. **`Organisation`**: Enterprise tenant boundary (`id`, `name`, `industry`).
2. **`Strategy`**: High-level strategic pillar (`time_horizon`, `status`).
3. **`ValueChain`**: Value creation domain (`strategy_id`).
4. **`Process`**: Operational business process (`value_chain_id`, `process_type`).
5. **`Activity`**: Granular task (`process_id`, `activity_type`: routine, analytical, review, manual, automated).
6. **`AIOpportunity`**: Targeted AI use case (`process_id`, `category`: automation, augmentation, optimization).
7. **`Role`**: Workforce job role (`department`).
8. **`Skill`**: Workforce competency (`skill_type`: data, domain, technical, ai_literacy).
9. **`Governance`**: Compliance & audit record (`ai_opportunity_id`, `category`, `risk_level`: high, medium, low).
10. **`TransformationInitiative`**: Strategic transformation program (`status`).
11. **`Dependency`**: Polymorphic directed graph edge (`source_entity_type`, `source_entity_id`, `target_entity_type`, `target_entity_id`, `relationship_type`).
12. **`TransformationAnalysis`**: Persistent audit record of scenario evaluations (`priority_score`, `priority_category`, `factor_scores`, `affected_entities`, `governance_findings`).

---

## 8. AI / LLM Architecture

The AI layer strictly uses structured Pydantic schema validation:

- **Provider Abstraction (`BaseLLMProvider`)**: Abstract interface defining `generate_structured(prompt, response_model)`.
- **Implementations**:
  - `OllamaProvider`: Connects to local Ollama server (`http://localhost:11434`, model `llama3.1`).
  - `MockLLMProvider`: High-speed local test fixture provider for unit and integration testing without external networks.
- **Scenario Extraction (`ScenarioExtractionService`)**: Converts natural language text into `ExtractedScenarioSpec` with SHA256 prompt caching.
- **Executive Explanation (`ExecutiveExplanationService`)**: Synthesizes narrative briefings grounded strictly in backend facts.
- **Prompt Injection Defense**: All user prompts are framed inside untrusted data boundaries with system prompts explicitly commanding the model to treat user text as data to analyze rather than instructions to follow.

---

## 9. RAG & Research Architecture

- **Local Embedding Provider (`app/rag/embeddings.py`)**: Computes local 384-dimensional normalized L2 unit vectors (`EMBEDDING_DIM = 384`) using a deterministic feature-hashing algorithm for zero-dependency local vector retrieval, requiring no external network API calls.
- **Recursive Text Chunker (`app/rag/chunker.py`)**: Splits research texts into 500-character segments with 50-character overlap while preserving source metadata.
- **Ingestion & Security (`app/rag/ingestion.py`)**: Enforces `ALLOWED_RESEARCH_DOMAINS` allowlist (`mckinsey.com`, `gartner.com`, `arxiv.org`, `hbr.org`, `retail-ai-research.org`, `synthetic.local`) to prevent Server-Side Request Forgery (SSRF) vulnerabilities.
- **Research Retriever (`app/rag/retriever.py`)**: Executes HNSW cosine distance search (`1 - (embedding <=> query)`). Filters candidate chunks against configurable similarity thresholds (`RAG_MIN_SIMILARITY_THRESHOLD = 0.30`).
- **Enterprise Semantic Retriever (`app/engines/semantic_retriever.py`)**: Embeds enterprise entity descriptions (`Process`, `AIOpportunity`, `ValueChain`) into PostgreSQL `enterprise_entity_embeddings`. Tracks `SHA256(searchable_text)` `content_hash` to detect and update stale embeddings automatically.

---

## 10. Deterministic Scoring Architecture

The `ScoringEngine` calculates an authoritative score ($0.0 - 100.0$) using 7 weighted factors:

$$\text{Priority Score} = \sum_{i=1}^{7} w_i \times S_i$$

| Factor | Weight ($w_i$) | Calculation Rationale |
| :--- | :---: | :--- |
| **Strategic Alignment** | **0.20** | Alignment with enterprise strategies, value chains, and active initiatives. |
| **Business Value** | **0.20** | Cost reduction, throughput increase, and revenue potential. |
| **AI Feasibility** | **0.15** | AI technology maturity and algorithmic complexity. |
| **Data Readiness** | **0.15** | Data availability, quality, and historical record volume. |
| **Expected Impact** | **0.15** | Scope of affected processes, activities, roles, and skills. |
| **Risk & Compliance** | **0.10** | Governance risk inversion (Low risk $\rightarrow$ High feasibility score). |
| **Dependency Complexity** | **0.05** | Graph prerequisite complexity and cycle risk. |

### Score Categories:
- **`HIGH`**: $\ge 75.0$
- **`MEDIUM`**: $50.0 - 74.9$
- **`LOW`**: $< 50.0$

---

## 11. Impact Propagation Engine

`ImpactEngine` executes a deterministic 2-hop Depth-First Search (DFS) across enterprise relationships:

```
AI Opportunity / Process
        │
        ├──► Value Chains (1st Hop)
        ├──► Connected Processes (1st Hop)
        └──► Activities (1st Hop)
                  │
                  ├──► Roles (2nd Hop via activity_roles)
                  └──► Skills (2nd Hop via activity_skills)
```

Surfaces complete structural metrics without relying on LLM inference.

---

## 12. Dependency Graph Engine

`DependencyEngine` analyzes directed polymorphic edges across `TransformationInitiative`, `AIOpportunity`, `Process`, and `ValueChain`:
- **Upstream Prerequisites**: Entities that must be transformed prior to launching target initiative.
- **Downstream Impact**: Entities affected if target initiative is altered or delayed.
- **Cycle Detection**: DFS stack tracking detects circular dependencies (e.g. $A \rightarrow B \rightarrow C \rightarrow A$) to prevent execution deadlocks.

---

## 13. Explainability & Information Trust Model

Every recommendation output exposes a 5-part audit breakdown:

| Audit Layer | Source / Mechanics | User Guarantee |
| :--- | :--- | :--- |
| **1. Persisted Facts** | PostgreSQL ORM domain models | Verified enterprise database facts. |
| **2. AI Inference** | LLM extraction & entity matching | Match confidence and extraction confidence scores explicitly shown. |
| **3. Research Evidence** | `pgvector` research chunks | Traceable citations with URLs and similarity values. |
| **4. Deterministic Calculation** | Phase 3 `ScoringEngine` | 100% mathematical calculation; zero LLM math. |
| **5. Executive Explanation** | `ExecutiveExplanationService` | Narrative briefing grounded in facts and research. |

---

## 14. Surprise Record Capability

The Surprise Record workflow evaluates **unseeded, novel natural language scenario prompts** (scenarios never explicitly defined in database tables) using hybrid retrieval:

```
Unseeded Natural Language Scenario Prompt
                  │
                  ▼
   1. ScenarioExtractionService (LLM Structured Spec)
                  │
                  ▼
   2. EntityMatcher (Tier 1 Exact Match & Tier 2 Fuzzy Match)
                  │  (If no exact match found)
                  ▼
   3. EnterpriseSemanticRetriever (pgvector Cosine Search)
                  │  (Dynamic match to nearest enterprise process)
                  ▼
   4. ResearchRetriever (pgvector Research Evidence Search)
                  │
                  ▼
   5. ScoringEngine + ImpactEngine (Deterministic Priority Score)
```

---

## 15. Three Validated Surprise Record Scenarios

All 3 scenarios are dynamically resolved without hardcoded scenario mappings:

1. **`"AI-powered warehouse slotting optimisation"`**:
   - Extracted Title: *"AI-Powered Warehouse Slotting Optimisation"*
   - Matched Process: `Store Inventory Management` (`Method: vector_semantic`, `Similarity: 0.27 LOW Confidence`)
   - Deterministic Score: **`78.2 / 100 (HIGH)`** | Citations: `2`
2. **`"AI-powered supplier risk prediction"`**:
   - Extracted Title: *"AI-Powered Supplier Risk Assessment"*
   - Matched Process: `Supplier Order Fulfillment` (`Method: exact`, `Similarity: 1.00 HIGH Confidence`)
   - Deterministic Score: **`81.8 / 100 (HIGH)`** | Citations: `1`
3. **`"AI-assisted workforce scheduling"`**:
   - Extracted Title: *"AI-Assisted Workforce Scheduling"*
   - Matched Process: `Workforce Scheduling` (`Method: exact`, `Similarity: 1.00 HIGH Confidence`)
   - Deterministic Score: **`64.2 / 100 (MEDIUM)`** | Citations: `2`

---

## 16. Multi-Tenant Organisation Isolation

TransformIQ enforces multi-tenant organisation isolation across all endpoints:
- Every query mandates `organisation_id`.
- Verified via integration test `test_intelligence_api_organisation_isolation_negative_tests`:
  - `Organisation B` queries return 0 priorities, 0 skills, and 0 governance records, proving complete data isolation from `Organisation A` (NovaMart).
  - Invalid organisation UUIDs return strict HTTP 404 Not Found responses.

---

## 17. Scalability Approach

- **Sub-Millisecond Vector Search**: Measured HNSW index search latency: **$0.48\text{ ms}$** (Warm query on local PostgreSQL pgvector).
- **Stateless API Design**: FastAPI routes remain completely stateless.
- **Indexed PostgreSQL Queries**: Composite indexes on `(organisation_id, id)` and foreign keys.
- **Deduplicated Priority Views**: `PriorityIntelligenceService` selects the latest authoritative analysis per unique enterprise entity, keeping execution history separate.
- **Pagination**: Endpoints enforce `limit` and `offset` pagination parameters.

---

## 18. Technology Stack

### Backend:
- **Language**: Python 3.11+ / Python 3.14
- **Framework**: FastAPI 0.111.0
- **ASGI Server**: Uvicorn 0.30.0
- **Database & Vector Extension**: PostgreSQL 16 + `pgvector` 0.5.1 (Docker image `ankane/pgvector:v0.5.1`)
- **ORM & Driver**: SQLAlchemy 2.0.30 (Asyncio) + `asyncpg` 0.29.0
- **Migrations**: Alembic 1.13.0
- **Data Validation & Settings**: Pydantic 2.7.0 + `pydantic-settings` 2.3.0
- **Testing**: Pytest 8.2.0 + `pytest-asyncio` + `pytest-cov`

### Frontend:
- **Build Tool & Framework**: Vite 8.2.0 + React 19.2.0 + TypeScript 6.0.2
- **Styling**: Vanilla CSS with glassmorphic tokens (Zero Tailwind dependency)

---

## 19. Setup Instructions for Windows / PowerShell

### Prerequisites:
- Windows 10/11 with PowerShell
- Python 3.11+ (Python 3.14 compatible)
- Node.js 18+ & `npm`
- Docker Desktop with Linux containers enabled

---

## 20. Docker / PostgreSQL / pgvector Setup

From project root in PowerShell:

```powershell
# 1. Start PostgreSQL + pgvector container
docker compose up -d db

# 2. Verify container status
docker compose ps
```

---

## 21. Backend Setup

```powershell
# Navigate to backend directory
cd backend

# Create Python virtual environment
python -m venv .venv

# Activate virtual environment in PowerShell
.\.venv\Scripts\Activate.ps1

# Upgrade pip and install dependencies
python -m pip install --upgrade pip
pip install -r requirements.txt
```

---

## 22. Frontend Setup

From `frontend` directory in PowerShell:

```powershell
cd ..\frontend

# Install frontend dependencies
npm install
```

---

## 23. Database Migration and Seed Instructions

From `backend` directory with virtual environment activated:

```powershell
cd ..\backend

# 1. Run Alembic migrations to create tables and vector indexes
alembic upgrade head

# 2. Seed NovaMart Enterprise synthetic dataset
python -m app.seed.novamart

# 3. Ingest synthetic research dataset and sync vector embeddings
python -m app.seed.research
```

---

## 24. Running Tests

From `backend` directory:

```powershell
# Run backend test suite (65 tests)
pytest tests/ -v
```

---

## 25. Production Frontend Build

From `frontend` directory:

```powershell
cd ..\frontend

# Run TypeScript check and Vite build
npm run build
```

---

## 26. Current Verification Results

- **Backend Pytest Test Suite**: **65 / 65 PASSED** (100% pass rate in 4.97s).
- **Frontend Production Build**: **Completed with 0 errors and 0 warnings** in 198ms.
- **HNSW Vector Search Latency**: **$0.48\text{ ms}$**.
- **Surprise Record Resolution**: 3/3 unseen scenarios dynamically resolved via pgvector.
- **Executive Dashboard Priority Ranking**:
  1. `Analysis of AI-Powered Demand Forecasting`: **86.2 / 100 (HIGH)**
  2. `AI-Powered Supplier Risk Assessment`: **81.8 / 100 (HIGH)**
  3. `Process Transformation Analysis: Demand Forecasting`: **81.8 / 100 (HIGH)**
  4. `AI-Powered Warehouse Slotting Optimisation`: **78.2 / 100 (HIGH)**
  5. `AI-Assisted Workforce Scheduling`: **64.2 / 100 (MEDIUM)**

---

## 27. Synthetic Research Evidence Disclaimer

> [!CAUTION]
> **Synthetic Demo Dataset Disclaimer**: Research documents ingested into `document_chunks` for demo purposes are synthetic datasets explicitly labeled **`"Synthetic Research Dataset — Demo Only"`**. They are provided for testing and evaluation of the RAG engine and are not independently verified published research.

---

## 28. Open-Source Component Usage & Software Licensing

Uses free/open-source components and can be reproduced without purchasing software licences.

---

## 29. AI Coding Tool Disclosure

TransformIQ was developed in pair programming with **Antigravity**, an agentic AI coding assistant designed by the Google DeepMind team working on Advanced Agentic Coding.

---

## 30. Limitations and Future Improvements

1. **Embedding Model Scalability**: Current local 384-dimensional embedding generator runs synchronously in Python; future revisions will delegate embedding computation to dedicated ONNX runtime background workers.
2. **Dynamic Graph Visualization**: The visual transformation graph currently renders key chain nodes; future frontend iterations will incorporate full WebGL-accelerated React Flow graph manipulation for 10,000+ node enterprise networks.
3. **Continuous Real-Time RAG**: Expand research ingestion allowlists to support automated RSS/API ingestion pipelines for enterprise regulatory compliance updates.