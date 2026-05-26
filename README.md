# Tech Challenge – API de Ordem de Serviço (Fase 3)


## Visão Geral

API RESTful desenvolvida para gerenciamento de oficina mecânica, permitindo:

- Cadastro de clientes
- Cadastro de veículos
- Gestão de peças
- Controle de estoque
- Criação e aprovação de ordens de serviço
- Autenticação via JWT
- Observabilidade com Datadog
- Deploy cloud-native em Kubernetes (EKS)

A aplicação foi construída utilizando arquitetura moderna baseada em:
- FastAPI
- PostgreSQL
- Kubernetes
- AWS
- Datadog

---

# Arquitetura

## Componentes Principais

- FastAPI
- PostgreSQL (RDS)
- AWS Lambda
- API Gateway
- Amazon EKS
- Datadog
- GitHub Actions
- Terraform

---

# Tecnologias Utilizadas

## Backend

| Tecnologia | Objetivo |
|---|---|
| FastAPI | Framework principal API |
| SQLAlchemy | ORM |
| Alembic | Migrations |
| PostgreSQL | Banco relacional |
| JWT | Autenticação |
| Uvicorn | ASGI Server |

---

## Cloud / Infraestrutura

| Tecnologia | Objetivo |
|---|---|
| AWS EKS | Kubernetes gerenciado |
| AWS RDS | Banco gerenciado |

---

## Observabilidade

| Tecnologia | Objetivo |
|---|---|
| Datadog | Observabilidade |
| ddtrace | Distributed tracing |
| JSON Logging | Logs estruturados |

---

# Estrutura do Projeto

```text
.
├── app
│   ├── api
│   ├── core
│   ├── models
│   ├── repositories
│   ├── schemas
│   ├── services
│   └── main.py
│
├── alembic
├── tests
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── README.md
```

---

# Execução Local

## Pré-requisitos

- Docker
- Docker Compose
- Python 3.12+
- PostgreSQL (opcional)
- Datadog Account (opcional)

---

# Configuração Variáveis Ambiente

Criar arquivo:

```text
.env
```

Exemplo:

```env
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=fiap
DATABASE_URL=postgresql://postgres:postgres@db:5432/fiap

SECRET_KEY=CHANGE_ME_SECRET
ALGORITHM=HS256

DD_API_KEY=YOUR_DATADOG_API_KEY

DD_SERVICE=fastapi-app
DD_ENV=local
DD_VERSION=1.0.0
DD_TRACE_ENABLED=true
DD_LOGS_INJECTION=true
```

---

# Subir Aplicação

```bash
docker compose up --build
```

---

# Aplicação

## Swagger

```text
http://localhost:8000/docs
```

---

# Banco de Dados

As migrations são executadas automaticamente no startup.

Para executar manualmente:

```bash
alembic upgrade head
```

---

# Execução via Python

## Instalar dependências

```bash
pip install -r requirements.txt
```

---

## Executar aplicação

```bash
uvicorn app.main:app --reload
```

---

# Deploy Cloud

## Pipeline CI/CD

O deploy é realizado automaticamente via:

```text
GitHub Actions
```

---

# Fluxo

1. Build Docker image
2. Push DockerHub/ECR
4. Deploy Kubernetes

---

# Deploy Kubernetes

## Aplicar manifests

```bash
kubectl apply -f k8s/
```

---

# Atualizar kubeconfig

```bash
aws eks update-kubeconfig \
  --name EKS-FIAP \
  --region us-east-1
```

---

# Observabilidade

## Recursos Monitorados

- Latência APIs
- Logs estruturados
- Distributed tracing
- CPU/Memória Kubernetes
- Healthchecks
- Erros aplicação
- Falhas ordens serviço

---

### 📂 Estrutura de Pastas Padrão

Com as mudanças realizadas, a arquitetura do projeto deve refletir a seguinte hierarquia de responsabilidades:

* **`app/routers/`**: Camada de interface. Contém apenas as definições de rotas (endpoints), tratamento de parâmetros de entrada e chamadas diretas aos *Services*.
* **`app/services/`**: Camada de aplicação (Cérebro). Onde reside toda a lógica de negócio, cálculos, orquestração de múltiplos repositórios e validações de regras.
* **`app/repositories/`**: Camada de infraestrutura. Focada estritamente em comandos de persistência (SQL/SQLAlchemy), realizando operações de CRUD puro.
* **`app/models/`**: Camada de domínio. Contém as definições das tabelas do banco de dados (SQLAlchemy Models) e tipos globais como os **Enums**.