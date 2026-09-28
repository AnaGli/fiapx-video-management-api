# video-management-api (k8s)

Manifests da API responsável por receber uploads de vídeo, publicar mensagens de processamento na fila e devolver o resultado ao usuário.

## Dependências externas

Este serviço **não** provisiona nenhuma infraestrutura. Antes de rodar `deploy.sh`, é preciso que o repositório [`video-infra-k8s`](../video-infra-k8s) já tenha sido aplicado — ele sobe RabbitMQ, LocalStack e o Postgres exclusivo desta API, todos no namespace `video-infra`.

## Uso

```bash
cp .env.example .env
# preencha DB_USER, DB_PASSWORD, RABBITMQ_USER, RABBITMQ_PASSWORD,
# AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY
# (as credenciais devem bater com o que foi configurado em video-infra-k8s)

./deploy.sh
```

## Acessando localmente

O Service é do tipo `ClusterIP` (só acessível de dentro do cluster). Para testar da sua máquina:

```bash
kubectl port-forward svc/video-management-api 8000:80
```

Depois acesse `http://localhost:8000`.

## Arquivos

```
configmap.yaml    # configuração não sensível (aponta para video-infra via DNS)
deployment.yaml     # a API em si, com readiness/liveness probes em /health
service.yaml         # ClusterIP, porta 80 -> 8000
hpa.yaml             # autoscaling horizontal
.env.example
deploy.sh
```

## O que não está neste repositório

- `rabbitmq.yaml` / `localstack.yaml` / `postgres.yaml` — tudo em `video-infra-k8s`
- `metrics.yaml` (metrics-server) — add-on de cluster, aplicado uma única vez, fora do ciclo de deploy de qualquer microsserviço

## Ajuste antes de usar

Troque a `image: video-management-api:latest` no `deployment.yaml` pelo nome real gerado pelo seu `docker build`, e garanta que o cluster local (Docker Desktop, kind, minikube) tenha acesso a essa imagem antes do deploy.
