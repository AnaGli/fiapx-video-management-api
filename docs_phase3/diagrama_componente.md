                           ┌─────────────────────────┐
                           │        Usuário          │
                           │  Web / Mobile / Swagger │
                           └────────────┬────────────┘
                                        │
                                        │ HTTPS
                                        ▼
                    ┌────────────────────────────────────┐
                    │         AWS API Gateway            │
                    │------------------------------------│
                    │ - Roteamento APIs                  │
                    │ - Exposição Swagger                │
                    │ - Proxy para Lambda/EKS            │
                    └────────────┬────────────┬──────────┘
                                 │            │
                  /login         │            │ /api/*
                                 │            │
                                 ▼            ▼

         ┌─────────────────┐         ┌──────────────────────────┐
         │ AWS Lambda Auth │         │      Amazon EKS          │
         │-----------------│         │--------------------------│
         │ - Autenticação  │         │ FastAPI Application      │
         │ - Geração JWT   │         │--------------------------│
         │ - CPF Validation│         │ - Clients API            │
         └────────┬────────┘         │ - Vehicles API           │
                  │                  │ - Service Orders API     │
                  │ JWT              │ - Approval API           │
                  │                  │ - Metrics API            │
                  │                  └────────────┬─────────────┘
                  │                               │
                  │                               │ SQLAlchemy
                  │                               ▼
                  │                  ┌──────────────────────────┐
                  │                  │      Amazon RDS          │
                  │                  │--------------------------│
                  │                  │ PostgreSQL               │
                  │                  │--------------------------│
                  │                  │ - clients                │
                  │                  │ - vehicles               │
                  │                  │ - service_orders         │
                  │                  │ - stock_movements        │
                  │                  └──────────────────────────┘
                  │
                  │
                  ▼
     ┌───────────────────────────────┐
     │ JWT Validation no FastAPI     │
     │-------------------------------│
     │ - Middleware Security         │
     │ - Token Validation            │
     │ - Authorization               │
     └───────────────────────────────┘


────────────────────────────────────────────────────────────────────


                   OBSERVABILIDADE E MONITORAMENTO


     ┌────────────────────────────────────────────────────┐
     │                    Datadog                        │
     │---------------------------------------------------│
     │                                                   │
     │ APM                                               │
     │ - Latência APIs                                   │
     │ - Distributed Tracing                             │
     │ - SQL Query Tracing                               │
     │                                                   │
     │ Logs                                              │
     │ - JSON Structured Logs                            │
     │ - Correlation ID                                  │
     │ - Error Tracking                                  │
     │                                                   │
     │ Infrastructure Monitoring                         │
     │ - CPU                                             │
     │ - Memory                                          │
     │ - Pod Health                                      │
     │ - Kubernetes Metrics                              │
     │                                                   │
     │ Alerts                                            │
     │ - Service Order Failures                          │
     │ - API Errors                                      │
     │ - Pod Restarts                                    │
     │ - High Latency                                    │
     └────────────────────────────────────────────────────┘
                               ▲
                               │
                               │
              ┌────────────────┴────────────────┐
              │                                 │
              │                                 │
              ▼                                 ▼

 ┌──────────────────────┐          ┌──────────────────────────┐
 │ Datadog Agent (EKS)  │          │ ddtrace + JSON Logging   │
 │----------------------│          │--------------------------│
 │ - DaemonSet          │          │ - Trace Injection        │
 │ - kube-state-metrics │          │ - Correlation IDs        │
 │ - Container Metrics  │          │ - Structured Logs        │
 │ - Pod Monitoring     │          │ - APM Tracing            │
 └──────────────────────┘          └──────────────────────────┘


────────────────────────────────────────────────────────────────────


                        CI/CD E INFRAESTRUTURA


         ┌───────────────────────────────────────┐
         │             GitHub Actions            │
         │---------------------------------------│
         │ - Build Docker Image                  │
         │ - Push ECR                            │
         │ - Terraform Apply                     │
         │ - Deploy Kubernetes                   │
         │ - Helm Deploy Datadog                 │
         └─────────────────┬─────────────────────┘
                           │
                           ▼

         ┌───────────────────────────────────────┐
         │              Terraform                │
         │---------------------------------------│
         │ - EKS                                │
         │ - RDS                                │
         │ - API Gateway                        │
         │ - Lambda                             │
         │ - Security Groups                    │
         │ - Networking                         │
         └───────────────────────────────────────┘