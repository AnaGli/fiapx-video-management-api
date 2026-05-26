# ADR-001 — Uso de Kubernetes (EKS) como Plataforma de Orquestração

## Status

Aceito

---

## Contexto

A aplicação precisava atender os seguintes requisitos arquiteturais:

- Escalabilidade horizontal
- Alta disponibilidade
- Execução containerizada
- Deploy automatizado
- Resiliência
- Suporte a observabilidade
- Evolução futura para microsserviços

Era necessário escolher entre:

- Docker Compose
- ECS/Fargate
- Kubernetes

---

## Decisão

Foi adotado:


Amazon EKS (Elastic Kubernetes Service)


como plataforma principal de orquestração.

---

## Justificativa

### Escalabilidade

O Kubernetes oferece:
- escalabilidade horizontal automática
- gerenciamento de replicas
- auto healing
- balanceamento interno

---

### Portabilidade

A solução permanece:
- cloud-native
- desacoplada da infraestrutura
- compatível com múltiplos provedores

---

### Observabilidade

Integração facilitada com:
- Datadog
- métricas Kubernetes
- tracing distribuído
- monitoramento de pods/nodes

---

### Resiliência

O Kubernetes fornece:
- restart automático containers
- healthchecks
- readiness/liveness probes
- rolling updates

---

## Consequências

### Positivas

- Alta disponibilidade
- Escalabilidade automática
- Arquitetura moderna
- Melhor resiliência

### Negativas

- Complexidade operacional maior
- Curva de aprendizado Kubernetes
- Custo operacional superior

---

# ADR-002 — Uso de HPA (Horizontal Pod Autoscaler)

## Status

Aceito

---

## Contexto

A aplicação precisava:
- escalar dinamicamente
- suportar variação de carga
- otimizar custos
- evitar desperdício recursos

Era necessário definir estratégia de escalabilidade.

---

## Decisão

Foi adotado:


Horizontal Pod Autoscaler (HPA)


baseado em:
- CPU
- memória

---

## Estratégia

O HPA monitora:
- uso CPU
- uso memória

e aumenta/reduz:
- quantidade de pods FastAPI

---

## Justificativa

### Elasticidade

Permite:
- aumentar capacidade sob carga
- reduzir recursos ociosos

---

### Integração Kubernetes

Integração nativa com:
- metrics-server
- EKS
- deployment replicas

---

### Redução de custo

Evita:
- superprovisionamento
- pods desnecessários

---

## Consequências

### Positivas

- Escalabilidade automática
- Melhor utilização recursos
- Maior disponibilidade

### Negativas

- Complexidade troubleshooting
- Possível cold start inicial

---

# ADR-003 — Padrão de Comunicação via API Gateway

## Status

Aceito

---

## Contexto

Era necessário expor APIs:
- publicamente
- com roteamento centralizado
- desacoplamento backend
- possibilidade futura de múltiplos serviços

Precisava-se definir:
- comunicação direta
- ingress controller
- API Gateway

---

## Decisão

Foi adotado:

```text
AWS API Gateway
```

como ponto central de entrada.

---

## Arquitetura

| Rota | Destino |
|---|---|
| /login | Lambda |
| /api/* | FastAPI no EKS |

---

## Justificativa

### Centralização

O API Gateway centraliza:
- autenticação
- roteamento
- exposição APIs

---

### Desacoplamento

Permite:
- trocar backends
- evoluir arquitetura
- adicionar novos serviços

---

### Segurança

Facilita:
- rate limiting
- políticas segurança
- integração futura WAF

---

## Consequências

### Positivas

- Arquitetura desacoplada
- Evolução simplificada
- Melhor governança APIs

### Negativas

- Camada adicional latência
- Complexidade configuração proxy

---

# ADR-004 — Uso de JWT Stateless para Autenticação

## Status

Aceito

---

## Contexto

A aplicação precisava:
- autenticação distribuída
- escalabilidade horizontal
- baixo acoplamento
- evitar sessão servidor

---

## Decisão

Foi adotado:


JWT Stateless Authentication


com:
- emissão via Lambda
- validação FastAPI

---

## Justificativa

### Escalabilidade

JWT elimina:
- armazenamento sessão
- sticky sessions
- sincronização sessão

---

### Arquitetura distribuída

Compatível com:
- múltiplos pods
- auto scaling
- APIs stateless

---

### Simplicidade

Fluxo simples:
1. Login
2. Emissão JWT
3. Validação token

---

## Consequências

### Positivas

- Escalabilidade horizontal
- Simplicidade operacional
- Menor acoplamento

### Negativas

- Revogação mais complexa
- Dependência proteção secret key

---

# ADR-005 — Estratégia de Observabilidade Centralizada com Datadog

## Status

Aceito

---

## Contexto

Era necessário monitorar:
- infraestrutura Kubernetes
- latência APIs
- erros aplicação
- tracing distribuído
- logs estruturados
- uptime

---

## Decisão

Foi adotado:


Datadog


como plataforma central de observabilidade.

---

## Componentes

| Componente | Objetivo |
|---|---|
| Datadog Agent | Métricas/logs |
| ddtrace | Distributed tracing |
| JSON logs | Logs estruturados |
| kube-state-metrics | Métricas cluster |

---

## Justificativa

### Observabilidade unificada

Centralização:
- logs
- métricas
- traces
- alertas

---

### Kubernetes Native

Integração completa com:
- EKS
- pods
- DaemonSets
- containers

---

### Distributed Tracing

Permite:
- rastrear requests
- identificar gargalos
- medir latência

---

## Consequências

### Positivas

- Alta visibilidade operacional
- Troubleshooting simplificado
- Monitoramento enterprise-grade

### Negativas

- Dependência SaaS
- Custos associados observabilidade

---

# ADR-006 — Uso de Logs Estruturados JSON

## Status

Aceito

---

## Contexto

A aplicação precisava:
- rastreabilidade
- correlação requests
- integração observabilidade
- logs pesquisáveis

---

## Decisão

Foi adotado:


Structured JSON Logging


com:
- correlation IDs
- integração Datadog

---

## Justificativa

### Padronização

Logs estruturados:
- facilitam parsing
- melhoram troubleshooting
- permitem queries avançadas

---

### Correlação

Uso de:

X-Correlation-ID


permite rastrear:
- requests
- traces
- logs
- erros

---

### Integração observabilidade

Compatível com:
- Datadog
- APM
- tracing distribuído

---

## Consequências

### Positivas

- Melhor troubleshooting
- Logs pesquisáveis
- Correlação distribuída

### Negativas

- Volume logs maior
- Estrutura logging mais complexa