```mermaid
flowchart TD

%% Users
U1[Tenant A User]
U2[Tenant B User]
U3[Tenant C User]

%% Gateway Layer
GW[API Gateway<br/>Auth + Tenant Detection + API Routing + Rate Limit]

%% Core API
API[FastAPI Core Service]

%% Tenant Router with centralised policies Zone Routing(LLM Gateway)
TR[LLM GW with central polcies with Zone Routing]

%% Tenant Isolation
subgraph TA[Tenant A]
     A1[FAISS Index A]
     A2[Region A Model]
end

subgraph TB[Tenant B]
    B1[FAISS Index B]
    B2[Region B Model]
end

subgraph TC[Tenant C]
    C1[FAISS Index C]
    C2[Region C Model]
end

%% Flow
U1 --> GW
U2 --> GW
U3 --> GW

GW --> API
API --> TR

TR --> TA
TR --> TB
TR --> TC
```
