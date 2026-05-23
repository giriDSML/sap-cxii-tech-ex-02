## 🎯 Overview

This project showcases a complete AI application stack featuring:

- **Natural Language to SQL**: Convert natural language queries into optimized SQL with context-aware prompting
- **Semantic Search**: FAISS-based vector search with blue-green deployment strategy for zero-downtime updates
- **Multi-LLM Provider Router**: OpenAI, Anthropic, Ollama, and custom local model integration with tenant-aware routing
- **Responsible AI**: PII redaction, request intent classification, and configurable guardrails
- **Enterprise Features**: Comprehensive logging, ETL pipeline, schema management, and Kubernetes deployment
- **Production-Ready**: Docker containerization, health checks, token logging, and audit trails

## 🏗️ Architecture

```
┌─────────────────────────────────────────┐
│          FastAPI Application             │
│         (Port 8000)                      │
├─────────────────────────────────────────┤
│  Routes                                  │
│  ├── /orders/* (Order CRUD operations)   │
│  ├── /ask (NL2SQL + semantic search)     │
│  ├── /healthz (Health checks)            │
│  └── /semantic/* (Vector search)         │
├─────────────────────────────────────────┤
│  Services Layer                          │
│  ├── AskService (Query orchestration)    │
│  ├── OrderService (Order management)     │
│  └── SemanticService (Vector search)     │
├─────────────────────────────────────────┤
│  AI/ML Core                              │
│  ├── NL2SQL Engine                       │
│  ├── LLM Router (tenant-aware)           │
│  ├── Embeddings Provider                 │
│  ├── PII Redaction                       │
│  └── Request Intent Classification       │
├─────────────────────────────────────────┤
│  Data Layer                              │
│  ├── SQLite Database                     │
│  ├── FAISS Vector Indexes (Blue/Green)   │
│  └── ETL Pipeline                        │
└─────────────────────────────────────────┘
```

## ⚡ Quick Start (Reviewer Setup)

### Environment Setup

This section explains the minimal steps required to run the system locally.
Follow this exact order to run the system.

git clone https://github.com/giriDSML/sap-cxii-tech-ex-02.git   
cd sap-cxii-tech-ex-02
### Create virutal environment
python -m venv venv  

### Activate environment:
source venv/bin/activate (Linux)           
venv\Scripts\activate (Windows)            

###  Install Dependencies
pip install -r requirements.txt         
### Configure Environment Variables
OPENAI_API_KEY=your_openai_key      
OPENAI_MODEL=gpt-4o-mini    
### Run ETL Pipeline ( Mandatory).
python etl.py load data/orders.csv
### Start FastAPI Server
uvicorn app:app --reload
### Service runs at
http://127.0.0.1:8000/docs

## 📚 API Endpoints

### Health & Status

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/healthz` | GET | Basic health check |


### Order Management

| Endpoint | Method | Description | Auth |
|----------|--------|-------------|------|
| ` /orders/customer/{customer_id}` | GET | List all orders for given customerID | Optional |
| ` /orders/stats` | GET | Get Order Stats | Optional |
| ` /orders/recent?days=N` | GET |Get Order for N recent days| Optional |


### AI Query Interface

| Endpoint | Method | Description |
|----------|--------|-------------|
| ` /ask` | POST | Submit natural language query |
| ` /semantic/search` | POST | Direct semantic search query |  
### Example for ask API
curl -X POST "http://127.0.0.1:8000/ask" \
-H "Content-Type: application/json" \
-d '{"query": "What is the total revenue from customer C123"}'

### Example for semantic/search API
curl -X POST "http://127.0.0.1:8000/semantic/search" \
-H "Content-Type: application/json" \
-d '{"query": "recent expensive orders", "top_k": 5}'


### Request Logging

All NL2SQL queries and semantic searches are logged in JSONL format:

```bash
# View request logs
tail -f logs/nl2sql_requests.jsonl | jq

# Example log entry
{
  "timestamp": "2024-05-22T10:30:45.123Z",
  "request_id": "req-12345",
  "tenant_id": "tenant_US",
  "query": "top 5 orders by value",
  "generated_sql": "SELECT * FROM orders ORDER BY amount DESC LIMIT 5",
  "execution_time_ms": 145,
  "tokens_used": 320,
  "provider": "openai"
}
```

### AI & Intelligence
- **NL2SQL Conversion**: Transforms natural language queries to parameterized SQL with schema awareness
- **Semantic Understanding**: Intent classification and contextual query analysis
- **Vector-Powered Search**: FAISS-indexed semantic similarity search over order data
- **Intelligent Routing**: Route queries to optimal LLM provider based on tenant and complexity

### Data Management
- **ETL Pipeline**: Complete extract, transform, load, and versioning pipeline
- **Schema Management**: Automated SQLite schema creation and migration
- **Blue-Green Indexing**: Zero-downtime vector index updates and deployment


### Enterprise & Operations
- **Tenant Multi-Tenancy**: Tenant-aware LLM routing with configurable provider mapping
- **PII Protection**: Automatic detection and masking of personally identifiable information
- **Structured Logging**: JSONL request logging with token tracking and audit trails
- **Health Monitoring**: Built-in health checks and readiness probes
- **Docker & Kubernetes**: Production-ready containerization with K8s manifests

### Responsible AI
- **Request Guardrails**: Configurable abuse prevention and request validation
- **Token Usage Tracking**: Monitor LLM token consumption for cost optimization
- **Intent Classification**: Classify user requests to ensure appropriate handling
- **Audit Trail**: Comprehensive logging for compliance and analysis

## 📁 Project Structure

```
sap-cxii-tech-ex-02/
├── app.py                        # FastAPI application entry point
├── etl.py                        # ETL orchestration
├── requirements.txt              # Python dependencies
├── Dockerfile                    # Multi-stage Docker build
├── README.md                     # This file
│
├── src/
│   ├── config.py                # Configuration & environment variables
│   ├── logging_utils.py         # Logging utilities
│   ├── utils.py                 # Shared utilities
│   │
│   ├── ai/                      # AI/ML core modules
│   │   ├── embeddings.py        # Embedding generation & provider
│   │   ├── llm_router.py        # Multi-provider LLM routing
│   │   ├── nl2sql.py            # Natural language to SQL engine
│   │   ├── pii_redaction.py     # PII detection & redaction
│   │   ├── prompts.py           # LLM prompt templates
│   │   ├── request_intent.py    # Intent classification
│   │   ├── responsible_ai_guardrails.py  # Request validation
│   │   ├── search_text_builder.py        # Query augmentation
│   │   ├── token_logging.py     # Token usage tracking
│   │   ├── vector_index.py      # FAISS indexing
│   │   └── llm_providers/       # LLM provider implementations
│   │       ├── base.py          # Base provider interface
│   │       ├── openai_provider.py
│   │       ├── anthropic_provider.py
│   │       ├── ollama_provider.py
│   │       └── localcustom_llm.py
│   │
│   ├── api/                     # REST API layer
│   │   ├── dependencies.py      # FastAPI dependency injection
│   │   ├── models.py            # Pydantic request/response models
│   │   ├── routes_ai.py         # AI query endpoints
│   │   ├── routes_orders.py     # Order management endpoints
│   │   └── routes_health.py     # Health & status endpoints
│   │
│   ├── db_layer/                # Database abstraction
│   │   ├── sqlite_client.py     # SQLite connection & operations
│   │   ├── schema_manager.py    # Schema creation & migrations
│   │   └── queries.py           # Predefined SQL queries
│   │
│   ├── etl/                     # Extract, Transform, Load
│   │   ├── contracts.py         # Data contracts & validation
│   │   ├── extract.py           # Data extraction
│   │   ├── transform.py         # Data transformation
│   │   ├── load.py              # Data loading
│   │   ├── summary.py           # Summary generation
│   │   └── versioning.py        # Version management
│   │
│   ├── search/                  # Semantic search services
│   │   ├── __init__.py
│   │   ├── embedding_provider.py
│   │   ├── index_builder.py
│   │   └── semantic_search_service.py
│   │
│   └── services/                # Business logic services
│       ├── ask_service.py       # Query orchestration
│       ├── order_service.py     # Order operations
│       ├── semantic_service.py  # Vector search
│       └── stats_service.py     # Statistics
│
├── artifacts/                   # Generated artifacts
│   └── semantic_index/          # FAISS vector indexes
│       ├── active_index.json    # Active index pointer
│       ├── blue/                # Blue deployment
│       │   ├── manifest.json
│       │   ├── metadata.json
│       │   └── orders.faiss
│       └── green/               # Green deployment (for updates)
│
├── data/                        # Data files
│   ├── order.csv               # Sample order data
│ 
│
├── db/                          # Database files
│   ├── schema.sql              # Database schema
│   └── orders.db               # SQLite database (generated)
│
├── k8s/                         # Kubernetes manifests
│   ├── configmap.yaml          # ConfigMap for environment
│   ├── deployment.yaml         # Deployment spec
│   └── service.yaml            # Service definition
│
├── logs/                        # Application logs
│   └── nl2sql_requests.jsonl   # Request audit trail
│
└── scripts/                     # Utility scripts
    ├── clean_runtime_data.py   # Clean runtime artifacts
    └── generate_orders_100_cases.py  # Generate test data
```


### Solution Writeup

# ETL Part
---

## 1. ETL Job Processing Logic

When the ETL job runs, it:

- Loads processed order records into SQLite (including required transformations and validations)
- Rebuilds the semantic search index after data load

### Handling Missing Values (Nulls)

For null values in order amount:

- A possible approach is to use the customer's historical average purchase amount
- However, based on the business rule, missing values are currently set to **0**

### Data Assumptions

- Orders are assumed to be immutable once submitted
- Therefore, historical versioning of orders is not maintained

---

# 4.a AI-Augmented Query Layer
---

### 4.a Model Selection Write-Up

The Text2SQL implementation uses **GPT-4o-mini** as the primary LLM.

---

### Key Reasons for Selection

#### 1. Context Window Support

GPT-4o-mini supports up to a **128K token context window**, which is sufficient for this use case involving:

- Database schema metadata  
- Table and column descriptions  
- Prompt instructions  
- Few-shot SQL examples included in the prompt  
- Natural language user queries  

This allows complete schema-aware reasoning in a single request.

---

#### 2. Cost Efficiency

- Input cost: **$0.15 per 1M tokens**  
- Output cost: **$0.60 per 1M tokens**

From an operational cost perspective, this is significantly lower compared to larger GPT models and other LLM providers such as Claude models.

---

#### 3. Strong Structured Reasoning Capability

The model performs well in structured generation tasks such as:

- SQL query construction  
- Schema understanding  
- Column mapping  
- Aggregation logic generation  
- Filter interpretation  

Its ~**82% MMLU score** indicates strong general reasoning ability while maintaining low cost and latency.

---

#### 4. Low Latency for Interactive Querying

- Typical first-token latency: **~200–600 ms**

This makes it suitable for real-time Text2SQL applications.

---

## Conclusion

Overall, GPT-4o-mini provides a strong balance of:

- Cost efficiency  
- Latency performance  
- Reasoning capability  
- Context handling ability  

This makes it well-suited for a constrained, schema-grounded Text2SQL system.


## 4.a System Prompt

> System Prompt used in the Text2SQL engine.  
> **Note**: We should reduce sending the full schema and should limit to only columns relevant in the context. Also PII features to masked in real world use case. We should also have SQL validation gate (post-generation but pre-execution) just to ensure LLM gives only SELECT query

---

### SYSTEM PROMPT

```text
SYSTEM PROMPT:

You are an enterprise-grade SQLite SQL generation agent.

Your responsibility is to convert natural language business questions into ONE safe, correct, and deterministic SQLite SELECT query using the provided schema.

--------------------------------------------------
CONTEXT
--------------------------------------------------

Available schema:
Table: orders
Columns: order_id TEXT, customer_id TEXT, order_date TEXT, amount_usd REAL, original_amount REAL, original_currency TEXT, updated_at TEXT

You DO NOT have access to actual data — only schema metadata.

IMPORTANT:
You must still generate SQL for ranking queries (highest, top, maximum) because SQL execution will resolve them.

--------------------------------------------------
CORE OBJECTIVE
--------------------------------------------------

Generate a single SQLite SELECT query that:
- accurately reflects the user’s intent
- uses only available schema columns
- follows strict safety, correctness, and formatting rules

--------------------------------------------------
OUTPUT FORMAT (STRICT CONTRACT)
--------------------------------------------------

Return VALID JSON ONLY:

{
  "can_answer": true or false,
  "reason": "short explanation",
  "sql": "single SQLite SELECT query OR empty string"
}

--------------------------------------------------
SQL SAFETY RULES
--------------------------------------------------

1. ONLY SELECT queries
2. NO INSERT, UPDATE, DELETE, DROP, ALTER
3. ONE query only
4. Use schema columns only
5. SQLite syntax only

--------------------------------------------------
AGGREGATION RULES
--------------------------------------------------

For TOTAL / SUM queries:

SELECT
SUM(amount_usd) AS total_revenue,
COUNT(*) AS order_count
FROM orders

--------------------------------------------------
ADVANCED AGGREGATION RULES (CRITICAL FIX)
--------------------------------------------------

Queries asking for:
- highest
- top
- maximum
- largest

MUST be handled using SQL, NOT rejected.

Use:

SELECT
customer_id,
SUM(amount_usd) AS total_revenue
FROM orders
GROUP BY customer_id
ORDER BY total_revenue DESC
LIMIT 1

NEVER reject these queries.

--------------------------------------------------
EXPLORATORY QUERIES
--------------------------------------------------

SELECT
order_id,
customer_id,
amount_usd,
order_date
FROM orders
ORDER BY order_date DESC

--------------------------------------------------
IDENTIFIER RULES
--------------------------------------------------

- Use only IDs present in question
- Never guess IDs

--------------------------------------------------
DATE RULES
--------------------------------------------------

"last N days" →
order_date >= date('now', '-N days')

--------------------------------------------------
WHEN TO REJECT
--------------------------------------------------

Reject ONLY if:
- Non-SQL request
- Column missing
- Invalid operation (non-SELECT)

DO NOT reject aggregation queries like "highest revenue"

--------------------------------------------------
FINAL CHECK
--------------------------------------------------

- JSON valid
- SQL valid
- SELECT only
- Matches intent
```

### 4.a. Retry Bad SQL Scenario

The retry loop was intentionally executed as a simulation, since the primary LLM is always  generating  correct SQL queries in normal execution.

### Bad SQL Used

```sql id="x0nq3k"
SELECT SUM(non_existing_amount_column) FROM orders;

SQL failed dry-run validation: no such column: non_existing_amount_column
Please generate a corrected SQLite query using only the available schema.

### Retry Correction
SELECT * FROM orders WHERE customer_id = 'CUSTOMER_REF_1';
```
## Guardrails, Security, Routing, and Observability

### 1. Pre-LLM Safety Guardrails

For this assessment, the following guardrails have been implemented:
- Input validation guardrails
- Prompt injection protection
- Jailbreak / safety bypass detection
- SQL injection protection at the input level
- Domain restriction guardrails
- Secret / credential leakage prevention
- Abusive content filtering

For a real-world enterprise deployment, additional guardrails can be added depending on the use case, data sensitivity, compliance requirements, and model provider risk profile.

---

### 2. PII Protection

No raw PII or sensitive business identifiers are shared with the LLM.

---

### 3. Authentication, Authorization, and API Controls
This assessment assumes that users invoking the APIs are already authenticated and authorized through enterprise security controls such as:

- OAuth-based authentication
- RBAC-based authorization
- API Gateway-level throttling and rate limiting
---
### 4. Agent Architecture Pattern

In a production enterprise system, this use case would typically follow a multi-agent architecture, where each responsibility is implemented as an independently scalable service.

---
### 5. Tenant-Based LLM Routing
Tenant-based LLM routing has been implemented in the architecture.

---
### 6. Observability and Monitoring
For this assessment, logging is implemented locally to keep the solution lightweight and self-contained.

---

# 4.b Semantic Search:
This project uses semantic (vector-based) search by enriching each record with additional textual features for embedding. We introduce Recency_Value (recent vs old based on date distribution) and Monetary_Value (high-value vs low-value based on amount distribution). 

We also derive a combined Recency_Monetary_Value label (e.g., Recent_HighValue, Recent_Cheap, Old_HighValue, Old_Cheap) using configurable thresholds such as 30 days for “recent”, 1 year for “old”, >$300 for “high value”, and <$50 for “low value”, enabling more accurate semantic retrieval through better clustering in vector space. 

Assumption is this search is not meant for SQL filter/analytics queries , its only a semantic search 

### Why FAISS 
FAISS index is used for scalable nearest-neighbor vector retrieval, avoiding brute-force NumPy comparison against every vector with O(n) linear search complexity while providing optimized similarity search and storage for embedding-based semantic search.

### Why sentence-transformers/all-MiniLM-L6-v2
The embedding model used is sentence-transformers/all-MiniLM-L6-v2, which generates compact 384-dimensional embeddings suitable for efficient storage and semantic search over structured order features.
It is lightweight, CPU-friendly, quick to load into memory, and provides good ROI for this assessment because it avoids external API cost while still supporting reliable similarity-based retrieval
### Index Rebuild
The system uses a blue/green index strategy where one index serves active search traffic while the inactive index is rebuilt during ETL.
After a successful rebuild, the active pointer is updated and the API reload endpoint switches the retriever to the new index without blocking in-flight requests.

# 4.d Architectural Extension
#### 1 Tenant Isolation for Vector Index

For tenant isolation in the vector index, there are two common options: a shared FAISS index with namespace filtering, or a separate index per tenant.

- **Shared index**: Lower memory and operational overhead, but requires strict filtering and introduces higher risk of data leakage or variable latency.
- **Per-tenant index**: Provides stronger data isolation, predictable latency, and simpler compliance boundaries, but increases memory usage and operational cost.

For an enterprise-grade design, the preferred approach is to use **regional control planes with per-tenant indexes deployed in the customer’s required geography**. This provides stronger isolation and compliance alignment, while accepting the trade-off of higher infrastructure and operational complexity.

#### 2 LLM Backend Routing per Tenant
Some enterprise customers may require requests to be routed to an on-premise or privately hosted model, such as a private Llama deployment, instead of a public cloud API.

In this architecture, the routing layer sits between the application/orchestration layer and the LLM providers. The application sends the tenant ID, prompt, and request context to an LLM router, and the router decides whether the request should be served by a cloud API, a private hosted endpoint, or an on-premise model. ( This is what we have done in this assessment)

This follows an **AI Gateway / LLM Gateway** pattern, where tenant-to-provider mapping is handled centrally. To keep the prompt layer model-agnostic, prompts are maintained in a provider-neutral format, while provider-specific differences such as API parameters, model names, authentication, and response parsing are handled inside the adapter layer.
#### 3 PII Guardrails in the NL-to-SQL Pipeline

The NL-to-SQL pipeline applies guardrails before the user question and schema context are sent to the LLM. These include schema minimization, PII redaction(prompt sanitisation when user himself asks with PII), and query intent validation to reduce exposure of sensitive information such as `customer_id` and monetary values.( as we did in Text2SQL agnet). To be more strict from security stand, we should have schema abstraction layer(i.e customer_id=attribute22),Row level and column level security even before going to LLM.

A strict zero-trust approach is followed for PII handling. Sensitive values are masked before reaching the LLM, and the model is instructed to use only the provided schema and not infer or generate hidden identifiers. In our assessment also we have masked the PIIs before sending to LLMs

If the LLM is a third-party cloud API, these controls are critical to reduce external data exposure. If the LLM is deployed on-premise, the exposure risk is reduced, but the same guardrails are still required to prevent any internal misuse and compromise
#### 4 Key Architectural Decision and Trade-off

My architectural decision is to use **per-tenant, region-bound isolation** as the default approach for retrieval and inference policy enforcement.

This means each tenant can have its own isolated vector index and LLM routing policy within the required geography, which improves data isolation, compliance alignment, and reduces the risk of cross-tenant data leakage.

The trade-off accepted is higher infrastructure cost and operational complexity compared to a shared-index model, but this is justified for enterprise workloads where security, regulatory compliance, and tenant-level isolation are more important than minimizing infrastructure footprint. A visual representation of this architecture is provided in the `multitenant.md` file



