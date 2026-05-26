````md
# RFC-001 — Escolha da Plataforma Cloud (AWS)

## Status

Aprovado

---

## Contexto

O sistema precisava atender os seguintes requisitos:

- Escalabilidade horizontal
- Execução containerizada
- APIs expostas publicamente
- Banco gerenciado
- Observabilidade
- Integração CI/CD
- Infraestrutura como código
- Serviços gerenciados para reduzir overhead operacional

As principais opções avaliadas foram:

- AWS
- Azure
- Google Cloud Platform (GCP)

---

## Decisão

Foi adotada a plataforma:

```text
Amazon Web Services (AWS)
```

---

## Serviços Utilizados

| Serviço | Objetivo |
|---|---|
| EKS | Orquestração Kubernetes |
| RDS | Banco relacional gerenciado |
| Lambda | Serviço de autenticação |
| API Gateway | Exposição e roteamento APIs |
| IAM | Controle de acesso |
| VPC/Security Groups | Networking e segurança |

---

## Justificativa

### 1. Integração nativa com Kubernetes

O Amazon EKS oferece:
- Kubernetes gerenciado
- alta disponibilidade
- integração nativa com networking AWS
- suporte enterprise

---

### 2. Redução de overhead operacional

Serviços gerenciados:
- RDS
- API Gateway
- Lambda

reduzem:
- manutenção
- patching
- failover manual

---

### 3. Escalabilidade

A arquitetura suporta:
- Horizontal Pod Autoscaling
- Auto scaling de nodes
- Escalabilidade independente por componente

---

### 4. Ecossistema e maturidade

A AWS possui:
- ampla documentação
- maturidade enterprise
- integração com Datadog
- compatibilidade Terraform

---

## Consequências

### Positivas

- Escalabilidade elevada
- Arquitetura cloud-native
- Observabilidade simplificada
- Deploy automatizado

### Negativas

- Complexidade inicial maior
- Custos potencialmente elevados em escala
- Curva de aprendizado Kubernetes/AWS

---

# RFC-002 — Escolha do Banco de Dados (PostgreSQL)

## Status

Aprovado

---

## Contexto

O sistema precisava armazenar:

- clientes
- veículos
- estoque
- ordens de serviço
- movimentações
- autenticação baseada em CPF

Era necessário:
- consistência transacional
- integridade relacional
- suporte SQL
- alta confiabilidade

---

## Decisão

Foi adotado:

```text
PostgreSQL no Amazon RDS
```

---

## Justificativa

### 1. Modelo relacional

As entidades possuem:
- relacionamentos fortes
- integridade referencial
- necessidade de joins

---

### 2. ACID

Ordens de serviço exigem:
- consistência
- transações
- rollback seguro

---

### 3. Compatibilidade com SQLAlchemy

Integração nativa com:
- SQLAlchemy
- Alembic
- FastAPI

---

### 4. Serviço gerenciado

O Amazon RDS fornece:
- backups automáticos
- monitoramento
- failover
- alta disponibilidade

---

## Alternativas Avaliadas

| Banco | Motivo descarte |
|---|---|
| MongoDB | Estrutura altamente relacional |
| DynamoDB | Complexidade relacional |
| MySQL | Menor aderência técnica/ecossistema |

---

## Consequências

### Positivas

- Forte consistência
- Facilidade modelagem
- Ecossistema maduro

### Negativas

- Escalabilidade horizontal mais complexa
- Maior consumo em joins pesados

---

# RFC-003 — Estratégia de Autenticação

## Status

Aprovado

---

## Contexto

O sistema precisava:
- autenticar clientes via CPF
- suportar APIs stateless
- permitir integração distribuída
- minimizar estado em servidor

---

## Decisão

Foi adotada autenticação baseada em:

```text
JWT (JSON Web Token)
```

com:
- geração via AWS Lambda
- validação na FastAPI

---

## Arquitetura

| Componente | Responsabilidade |
|---|---|
| Lambda Auth | Emissão JWT |
| API Gateway | Exposição endpoint login |
| FastAPI | Validação token |
| Middleware JWT | Autorização |

---

## Justificativa

### 1. Arquitetura stateless

JWT elimina:
- sessões servidor
- sticky sessions
- armazenamento distribuído sessão

---

### 2. Escalabilidade

A autenticação pode:
- escalar horizontalmente
- funcionar em múltiplos pods

---

### 3. Separação responsabilidades

A Lambda centraliza:
- emissão token
- autenticação CPF

A FastAPI:
- valida autorização
- aplica regras negócio

---

### 4. Integração cloud-native

Lambda reduz:
- custo ocioso
- gerenciamento infraestrutura

---

## Segurança

Os tokens utilizam:
- assinatura HS256
- expiração
- validação obrigatória

---

## Alternativas Avaliadas

| Estratégia | Motivo descarte |
|---|---|
| Session-based auth | Não escalável |
| OAuth completo | Complexidade excessiva |
| API Keys | Sem identidade usuário |

---

## Consequências

### Positivas

- Escalabilidade
- Stateless architecture
- Integração simples APIs

### Negativas

- Revogação JWT mais complexa
- Necessidade proteção secret key

---

# RFC-004 — Estratégia de Observabilidade

## Status

Aprovado

---

## Contexto

O sistema precisava monitorar:

- latência APIs
- erros
- infraestrutura Kubernetes
- logs estruturados
- tracing distribuído
- uptime
- falhas negócio

---

## Decisão

Foi adotado:

```text
Datadog
```

com:
- Datadog Agent
- APM
- Structured Logging
- Distributed Tracing

---

## Componentes

| Componente | Objetivo |
|---|---|
| Datadog Agent | Coleta métricas/logs |
| ddtrace | Distributed tracing |
| JSON logging | Logs estruturados |
| kube-state-metrics | Métricas Kubernetes |

---

## Justificativa

### 1. Observabilidade unificada

Centralização de:
- métricas
- logs
- traces
- alertas

---

### 2. Integração Kubernetes

Suporte nativo:
- EKS
- containers
- DaemonSets
- HPA

---

### 3. Distributed tracing

Permite:
- rastrear requests
- medir latência
- identificar gargalos

---

### 4. Logs estruturados

Facilitam:
- troubleshooting
- correlação
- monitoramento negócio

---

## Consequências

### Positivas

- Alta visibilidade operacional
- Troubleshooting simplificado
- Monitoramento enterprise-grade

### Negativas

- Dependência ferramenta SaaS
- Custos variáveis conforme volume logs/traces
````
