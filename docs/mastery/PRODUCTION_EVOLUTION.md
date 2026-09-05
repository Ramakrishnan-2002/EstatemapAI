# EstateMap AI — Production Evolution Roadmap

This document outlines the architectural roadmap for transitioning EstateMap AI from a single-node modular monolith portfolio project to a distributed, multi-region production platform handling millions of daily active users.

---

## 1. Clear Architecture Separation: Current vs. Future

```
CURRENT (Single-Node Modular Monolith)
- Docker Compose Network
- Single PostgreSQL 16 + PostGIS Primary
- Single Redis 7 In-Memory Instance
- Self-Hosted OSRM HTTP Engine
- In-Process Python Asynchronous Worker Pool
- Local Ollama / Google Gemini AI Router

                    │
                    ▼  (Evolution to Enterprise Scale)

FUTURE (Distributed High-Availability Cloud Deployment)
- Kubernetes (EKS / GKE) Auto-Scaling Worker Pods
- AWS Aurora PostgreSQL Multi-AZ (1 Writer + 3 Read Replicas)
- AWS ElastiCache Redis Cluster (3 Shards + Multi-AZ Failover)
- Distributed Multi-Zone OSRM Routing Fleet
- Apache Kafka Event Bus (Listing Ingestion & Analytics Pipeline)
- OpenSearch Cluster (Fuzzy Linguistic Search & Document Retrieval)
- Cloudflare Enterprise WAF + Anycast CDN
```

---

## 2. Phase-by-Phase Production Evolution

### Stage 1: High Availability & Database Read Replicas (100k -> 500k DAU)
1. **Database Tier**: Migrate to AWS Aurora PostgreSQL Multi-AZ with PostGIS. Configure 1 Writer instance and 2 Reader replicas. Use PgBouncer connection pooling to handle thousands of concurrent client connections.
2. **Cache Tier**: Upgrade to AWS ElastiCache for Redis Cluster with automatic multi-AZ failover and data encryption at rest.
3. **Application Tier**: Containerize backend into AWS ECS Fargate or Kubernetes with Horizontal Pod Autoscalers (HPA) scaling on CPU/Memory and request queue depth.

### Stage 2: Asynchronous Event Pipelines & Ingestion (500k -> 2M DAU)
1. **Apache Kafka Event Bus**:
   * Topic `property.listings.created`: Triggers asynchronous image optimization, CDN distribution, and spatial indexing.
   * Topic `user.search.analytics`: Streams user search queries to clickhouse/BigQuery for analytics without blocking the search API.
2. **Object Storage & CDN**: Store listing images on Amazon S3 / Cloudflare R2 with automatic WebP transformation and Cloudflare CDN caching.

### Stage 3: Dedicated Full-Text & Fuzzy Linguistic Search (2M -> 10M DAU)
1. **OpenSearch / Elasticsearch Cluster**: Integrate OpenSearch via Change Data Capture (Debezium + Kafka Connect) from PostgreSQL. Use OpenSearch for fuzzy phonetic and typo-tolerant search ("Indra Ngr" -> "Indiranagar"), while keeping PostGIS for authoritative spatial polygon and bounding-box queries.
2. **Learning-to-Rank (LTR) Machine Learning**: Train an XGBoost / LambdaMART ranking model on accumulated user interaction logs (clicks, dwell time, favorites, contact owner inquiries), using deterministic ranking scores as a primary feature.
