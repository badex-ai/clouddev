# Project Name

[![Build Status](https://img.shields.io/badge/build-passing-brightgreen)](link)
[![License](https://img.shields.io/badge/license-MIT-blue)](LICENSE)
[![Version](https://img.shields.io/badge/version-1.0.0-orange)](link)

> A brief, compelling description of what your application does and why it matters. Keep it to 1-2 sentences.

## Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
  - [Development](#development)
- [Project Structure](#project-structure)
- [Deployment](#deployment)
- [Testing](#testing)
- [Contributing](#contributing)
- [License](#license)

## Overview

This project showcases a production-grade microservices architecture deployed on Kubernetes, designed to demonstrate modern cloud-native development practices and infrastructure-as-code principles. The application leverages AWS Elastic Kubernetes Service (EKS) for orchestration while providing a fully-functional local development environment using MicroK8s.
What Makes This Project Special
Cloud-Native Architecture: Built from the ground up as a distributed system with independent, scalable microservices that communicate asynchronously through message queues and cache layers.
Infrastructure as Code: Complete infrastructure automation using Terraform for AWS resource provisioning and Helm charts for Kubernetes deployment management, ensuring reproducible and version-controlled infrastructure.
Development Flexibility: Seamless transition between local development (Docker Compose), local Kubernetes testing (MicroK8s), and cloud deployment (AWS EKS) without code changes.



### Tech Stack

**Frontend**
- Next.js with TypeScript
- React components with shadcn/ui
- Tailwind CSS
- Jest for testing
- Sentry for error monitoring

**Backend**
- Python/FastAPI
- PostgreSQL database
- Alembic for migrations
- Celery for async task processing
- pytest for testing

**Infrastructure**
- Docker & Docker Compose
- Kubernetes (K8s)
- ArgoCD for GitOps
- Terraform for IaC

**Infrastructure components**
- Cloudwatch
- Secret manager
- Elasticache
- RDS
- S3 for terraform state storage


## Architecture

```
┌─────────────────┐         ┌─────────────────┐         ┌─────────────────┐
│                 │         │                 │         │                 │
│    Frontend     │────────▶│     Backend     │────────▶│    Database     │
│   (Next.js)     │         │   (FastAPI)     │         │  (PostgreSQL)   │
│                 │         │                 │         │                 │
└─────────────────┘         └─────────────────┘         └─────────────────┘
                                     │
                                     │
                            ┌────────▼────────┐
                            │                 │
                            │  Celery Worker  │
                            │                 │
                            └─────────────────┘
```



## Getting Started

### Prerequisites

Before you begin, ensure you have the following installed:

- Docker (version 20.10+)
- Docker Compose (version 2.0+)
- Node.js (version 18+)
- Python (version 3.11+)
- Kubernetes CLI (kubectl) - for K8s deployment
- Task (optional, for running Taskfile commands)

### Installation

1. Clone the repository:
```bash
git clone https://github.com/your-org/your-repo.git
cd your-repo
```

2. Copy environment files:
```bash
cp .env.example .env
```

3. Configure environment variables in `.env` file

### Development

#### Using Docker Compose (Recommended)

```bash
# Start all services in development mode
docker-compose -f docker-compose.dev.yaml up

# View logs
docker-compose -f docker-compose.dev.yaml logs -f

# Stop services
docker-compose -f docker-compose.dev.yaml down
```

#### Local Development

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```
Access at: http://localhost:3000

**Backend:**
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```
Access at: http://localhost:8000

**Celery Worker:**
```bash
cd backend
celery -A celery_worker worker --loglevel=info
```
#### Local k8s development
YOu can download Microk8s and run the helm files on it using the Taskfile

#### Using Taskfile

```bash
# List available tasks
task --list

# Run specific task
task setup-k8s-local
```

## Project Structure

```
.
├── backend/                 # Python/FastAPI backend
│   ├── alembic/            # Database migrations
│   ├── config/             # Configuration files
│   ├── controllers/        # Business logic
│   ├── models/             # Database models
│   ├── routes/             # API endpoints
│   ├── schemas/            # Pydantic schemas
│   ├── tests/              # Backend tests
│   ├── utils/              # Utility functions
│   └── main.py             # Application entry point
│
├── frontend/               # Next.js frontend
│   ├── app/                # Next.js app directory
│   ├── components/         # React components
│   ├── contexts/           # React contexts
│   ├── hooks/              # Custom React hooks
│   ├── lib/                # Utility libraries
│   ├── public/             # Static assets
│   └── __tests__/          # Frontend tests
│
├── infrastructure/         # DevOps & Infrastructure
│   ├── k8s/               # Kubernetes manifests
│   ├── scripts/           # Automation scripts
│   ├── security/          # Security configs
│   └── terraform/         # Terraform IaC
│
├── docker-compose.*.yaml  # Docker Compose configs
└── Taskfile.yaml          # Task automation
```

## Deployment

The application supports multiple deployment environments:

- **Development:** `docker-compose.dev.yaml`
- **Development k8s:** `docker-compose.devk8s.yaml`
- **Staging:** `docker-compose.staging.yaml`
- **Production:** `docker-compose.production.yaml`

### Local development

```bash
docker compose \
  --env-file example.env \
  -f docker-compose.yml \
  -f docker-compose.dev.yaml \
  up -d
```

####

```bash
docker compose \
  --env-file example.env \
  -f docker-compose.yml \
  -f docker-compose.devk8s.yaml \
  up -d
```

### Docker Deployment

```bash
# Build images
docker-compose build
```

### Kubernetes Deployment

```bash
# Set up local K8s
./localk8sSetup



# Apply K8s manifests
kubectl apply -f infrastructure/k8s/

```

Taskfile.yaml (contains tasks methods you can apply ) 

### Terraform Infrastructure

```bash
cd infrastructure/terraform
terraform init
terraform plan -var-file="staging.tfvars" -out=tfplan
terraform apply tfplan

## Monitoring & Observability

- **Error Tracking:** Sentry (configured in frontend)
- **Logging:** Centralized logging in cloudwatch



## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.


---

**Made by Me **