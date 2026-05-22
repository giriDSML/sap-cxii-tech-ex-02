# SAP CX II AI Technical Exercise

An enterprise-grade AI-powered order management system that demonstrates production-ready architecture for intelligent order querying. Combines natural language processing, semantic search, and multi-provider LLM integration to enable intelligent analysis of customer orders with responsible AI safeguards.

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

## 🚀 Key Features

### AI & Intelligence
- **NL2SQL Conversion**: Transforms natural language queries to parameterized SQL with schema awareness
- **Semantic Understanding**: Intent classification and contextual query analysis
- **Vector-Powered Search**: FAISS-indexed semantic similarity search over order data
- **Intelligent Routing**: Route queries to optimal LLM provider based on tenant and complexity

### Data Management
- **ETL Pipeline**: Complete extract, transform, load, and versioning pipeline
- **Schema Management**: Automated SQLite schema creation and migration
- **Blue-Green Indexing**: Zero-downtime vector index updates and deployment
- **Data Versioning**: Track and manage data versions across transformations

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
│   ├── processed/              # Transformed data
│   └── sample/                 # Sample datasets
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

## 🛠️ Technology Stack

| Category | Technology |
|----------|-----------|
| **Framework** | FastAPI 0.115.0 |
| **Server** | Uvicorn 0.30.6 |
| **Database** | SQLite with SQLAlchemy 2.0.35 |
| **Vector Search** | FAISS CPU 1.8.0 |
| **Embeddings** | Sentence-Transformers 3.1.1 |
| **LLM Providers** | OpenAI 1.47.0, Anthropic, Ollama |
| **Data Processing** | Pandas 2.2.2, NumPy 1.26.4 |
| **Validation** | Pydantic 2.9.2 |
| **Containerization** | Docker (multi-stage build) |
| **Orchestration** | Kubernetes |
| **Testing** | pytest 8.3.3 |
| **HTTP Client** | httpx 0.27.2 |

## 🔧 Configuration

Environment variables control the application behavior. Create a `.env` file or set them directly:

```env
# Database
DB_PATH=db/orders.db
NL2SQL_LOG_PATH=logs/nl2sql_requests.jsonl

# Tenant Routing (maps tenants to LLM providers)
DEFAULT_TENANT_ID=tenant_US
# TENANT_LLM_MAP = {"tenant_KSA": "ollama", "tenant_US": "openai", "tenant_EU": "openai"}

# OpenAI Configuration
OPENAI_API_KEY=sk-proj-...
OPENAI_MODEL=gpt-4o-mini

# Ollama Configuration (local LLM)
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.1:8b

# Anthropic Configuration (optional)
ANTHROPIC_API_KEY=
ANTHROPIC_MODEL=claude-3-5-sonnet-20241022

# Responsible AI
MAX_QUESTION_LENGTH=1000
MIN_QUESTION_LENGTH=3
ENABLE_ABUSE_GUARDRAILS=true
```

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Docker (optional, for containerization)
- OpenAI API key (or Ollama for local LLM setup)
- Git (for version control)

### Step 1: Clone & Install Dependencies

```bash
# Navigate to project directory
cd sap-cxii-tech-ex-02

# Create virtual environment (optional but recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install all required packages
pip install -r requirements.txt
```

### Step 2: Configure Environment

Create a `.env` file in the project root or set environment variables:

```bash
# LLM Provider Keys
export OPENAI_API_KEY="sk-proj-your-api-key"
export ANTHROPIC_API_KEY="your-anthropic-key"

# Ollama (for local LLM)
export OLLAMA_BASE_URL="http://localhost:11434"
export OLLAMA_MODEL="llama3.1:8b"

# Database
export DB_PATH="db/orders.db"
export NL2SQL_LOG_PATH="logs/nl2sql_requests.jsonl"

# Tenant Configuration
export DEFAULT_TENANT_ID="tenant_US"

# Responsible AI
export ENABLE_ABUSE_GUARDRAILS="true"
export MAX_QUESTION_LENGTH="1000"
```

### Step 3: Initialize Database & Indexes

```bash
# Ensure required directories exist
mkdir -p db logs artifacts/semantic_index

# Initialize database schema
python -c "from src.db_layer.schema_manager import SchemaManager; SchemaManager().create_schema()"

# Load sample data (optional)
python etl.py
```

### Step 4: Build Semantic Indexes

```bash
# Build FAISS vector indexes from order data
python -c "from src.search.index_builder import build_semantic_index; build_semantic_index()"
```

### Step 5: Run the Application

```bash
# Development mode (auto-reload enabled)
uvicorn app:app --reload --host 0.0.0.0 --port 8000

# Production mode
uvicorn app:app --host 0.0.0.0 --port 8000 --workers 4
```

The application will start at `http://localhost:8000`

- **API Documentation**: Visit `http://localhost:8000/docs` (Swagger UI)
- **ReDoc**: Visit `http://localhost:8000/redoc` (ReDoc documentation)
- **Health Check**: `http://localhost:8000/healthz`

## 📚 API Endpoints

### Health & Status

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/healthz` | GET | Basic health check |
| `/health` | GET | Detailed health status |
| `/health/ready` | GET | Readiness probe for K8s |

### Order Management

| Endpoint | Method | Description | Auth |
|----------|--------|-------------|------|
| `/orders` | GET | List all orders (with pagination & filtering) | Optional |
| `/orders` | POST | Create new order | Optional |
| `/orders/{order_id}` | GET | Get specific order details | Optional |
| `/orders/{order_id}` | PUT | Update order information | Optional |
| `/orders/{order_id}` | DELETE | Delete an order | Optional |
| `/orders/search` | POST | Semantic search across orders | Optional |

### AI Query Interface

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/ask` | POST | Submit natural language query |
| `/ask/nl2sql` | POST | Convert query to SQL (debug endpoint) |
| `/semantic/search` | POST | Direct semantic search query |

### Example Requests

**Natural Language Query:**
```bash
curl -X POST "http://localhost:8000/ask" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What are the top 5 orders by value?",
    "tenant_id": "tenant_US"
  }'
```

**Create Order:**
```bash
curl -X POST "http://localhost:8000/orders" \
  -H "Content-Type: application/json" \
  -d '{
    "customer_id": "C123",
    "order_date": "2024-05-22",
    "total_amount": 1500.00,
    "items": [...]
  }'
```

**Semantic Search:**
```bash
curl -X POST "http://localhost:8000/semantic/search" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "expensive orders from valued customers",
    "limit": 10
  }'
```

## 🐳 Docker Deployment

### Build Docker Image

```bash
# Build using multi-stage build
docker build -t sap-ai-orders:latest .

# Run container
docker run -p 8000:8000 \
  -e OPENAI_API_KEY="sk-proj-..." \
  -e DB_PATH="/app/db/orders.db" \
  -v $(pwd)/db:/app/db \
  -v $(pwd)/logs:/app/logs \
  -v $(pwd)/artifacts:/app/artifacts \
  sap-ai-orders:latest
```

### Docker Compose (if available)

```bash
docker-compose up -d
docker-compose logs -f
docker-compose down
```

## ☸️ Kubernetes Deployment

### Prerequisites
- kubectl configured with cluster access
- Docker image pushed to registry

### Deploy to Kubernetes

```bash
# Apply ConfigMap with environment configuration
kubectl apply -f k8s/configmap.yaml

# Deploy the application
kubectl apply -f k8s/deployment.yaml

# Expose service
kubectl apply -f k8s/service.yaml

# Verify deployment
kubectl get pods
kubectl get svc
kubectl logs -f deployment/sap-ai-orders
```

### Scaling

```bash
# Scale to 3 replicas
kubectl scale deployment/sap-ai-orders --replicas=3

# Auto-scaling (requires metrics server)
kubectl autoscale deployment sap-ai-orders --min=2 --max=10 --cpu-percent=80
```

### Port Forwarding

```bash
kubectl port-forward svc/sap-ai-orders 8000:8000
```

## 📊 Logging & Monitoring

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

### Token Tracking

Monitor LLM usage per provider:

```bash
# Check token log in logs/nl2sql_requests.jsonl
grep "tokens_used" logs/nl2sql_requests.jsonl | jq '.tokens_used'
```

### Application Metrics

- **Response Times**: Track in logs via `execution_time_ms`
- **Error Rates**: Query failures logged with error details
- **Provider Usage**: Distribute queries across OpenAI, Anthropic, Ollama
- **Index Health**: Monitor FAISS index size and freshness

## 🔒 Responsible AI & Security

### PII Protection

```python
# Automatic PII redaction in logs
# Masks: SSN, credit cards, email, phone numbers
# Location: src/ai/pii_redaction.py
```

### Request Validation

```python
# Request length validation
MIN_QUESTION_LENGTH = 3
MAX_QUESTION_LENGTH = 1000

# Intent classification
# Ensures requests align with business logic
# Blocks potential SQL injection or abuse
```

### Guardrails

```python
# src/ai/responsible_ai_guardrails.py provides:
- Request sanitization
- SQL injection prevention
- Token limit enforcement
- Rate limiting per tenant
```

### Audit & Compliance

- All requests logged with tenant context
- Timestamp and execution details captured
- Generated SQL stored for review
- Response time and token usage tracked

## 🧪 Testing & Development

### Run Tests

```bash
# Install test dependencies
pip install pytest pytest-cov

# Run all tests
pytest

# Run specific module tests
pytest tests/test_nl2sql.py -v

# Generate coverage report
pytest --cov=src tests/ --cov-report=html
```

### Local Development Setup

```bash
# 1. Install development dependencies
pip install -r requirements.txt
pip install black flake8 mypy

# 2. Code formatting
black src/

# 3. Linting
flake8 src/

# 4. Type checking
mypy src/

# 5. Run tests with coverage
pytest --cov=src tests/
```

### Database Management

```bash
# Reset database (⚠️ WARNING: Deletes all data)
rm db/orders.db
python -c "from src.db_layer.schema_manager import SchemaManager; SchemaManager().create_schema()"

# Clean runtime artifacts
python scripts/clean_runtime_data.py

# Generate test data
python scripts/generate_orders_100_cases.py
```

## 🔧 Advanced Configuration

### Tenant Routing

Configure which LLM provider each tenant uses:

```python
# src/config.py
TENANT_LLM_MAP = {
    "tenant_KSA": "ollama",          # Use local Ollama
    "tenant_US": "openai",           # Use OpenAI
    "tenant_EU": "openai",           # Use OpenAI
}
```

### LLM Model Selection

```env
# OpenAI
OPENAI_MODEL=gpt-4o-mini            # Fast, cost-effective
OPENAI_MODEL=gpt-4                   # More capable

# Anthropic
ANTHROPIC_MODEL=claude-3-5-sonnet-20241022

# Ollama (local, free)
OLLAMA_MODEL=llama3.1:8b
OLLAMA_MODEL=mistral:latest
```

## 🐛 Troubleshooting

### Common Issues

**Issue**: `ModuleNotFoundError: No module named 'openai'`
```bash
# Solution: Reinstall dependencies
pip install --upgrade -r requirements.txt
```

**Issue**: `Connection refused: localhost:11434` (Ollama)
```bash
# Solution: Start Ollama service
ollama serve
# In another terminal, pull a model:
ollama pull llama3.1:8b
```

**Issue**: `FAISS index not found`
```bash
# Solution: Rebuild indexes
python -c "from src.search.index_builder import build_semantic_index; build_semantic_index()"
```

**Issue**: Database locked error
```bash
# Solution: Ensure only one process accesses the database
# Check running processes and close duplicates
lsof | grep orders.db
```

### Debug Mode

```bash
# Enable verbose logging
export LOG_LEVEL=DEBUG
uvicorn app:app --reload --log-level debug
```

## 📖 Documentation & References

### Core Components
- **[NL2SQL Engine](src/ai/nl2sql.py)** - Query-to-SQL translation logic
- **[Semantic Search](src/search/semantic_search_service.py)** - Vector similarity search
- **[LLM Router](src/ai/llm_router.py)** - Provider selection and fallback
- **[ETL Pipeline](src/etl/)** - Data extraction, transformation, loading
- **[Database Layer](src/db_layer/)** - SQLite management and queries

### External Resources
- [FAISS Documentation](https://github.com/facebookresearch/faiss)
- [FastAPI Guide](https://fastapi.tiangolo.com/)
- [OpenAI API Docs](https://platform.openai.com/docs)
- [Anthropic Documentation](https://www.anthropic.com/docs)
- [Sentence Transformers](https://www.sbert.net/)

## 🤝 Contributing

1. Create a feature branch: `git checkout -b feature/my-feature`
2. Make changes and add tests
3. Run linting: `black src/ && flake8 src/`
4. Run tests: `pytest`
5. Commit and push: `git push origin feature/my-feature`
6. Open a pull request

## 📝 License

SAP Internal - Technical Exercise

---

**Project Status**: Active Development  
**Last Updated**: May 2026  
**Version**: 1.0.0  
**Python Version**: 3.11+  
**Maintainer**: SAP AI Team

