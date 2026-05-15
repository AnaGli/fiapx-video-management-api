# Tech Challenge – API de Ordem de Serviço

Este projeto é uma **API REST** desenvolvida com FastAPI, SQLAlchemy, PostgreSQL, Docker e Alembic, com o objetivo de gerenciar ordens de serviço de uma oficina, incluindo clientes, veículos, serviços, peças, orçamento e acompanhamento de status.

---

## 🎯 Objetivos do Projeto

* **Gerenciar clientes** identificados por CPF/CNPJ, com validação de dados sensíveis.
* **Gerenciar veículos** associados a clientes (placa, marca, modelo, ano).
* **Gerenciar serviços e peças/insumos**, incluindo controle de estoque.
* **Criar e acompanhar Ordens de Serviço (OS)** com:
    * Inclusão de serviços e peças.
    * Geração automática de orçamento.
    * Fluxo de status bem definido.
    * Aprovação do orçamento pelo cliente via CPF.
* **Monitorar tempo médio** de execução das ordens de serviço.
* **Disponibilizar uma API** preparada para testes automatizados e análise de qualidade.

---

## 🧱 Stack Tecnológica

* **Linguagem:** Python 3.12
* **Framework:** FastAPI
* **ORM:** SQLAlchemy
* **Migrations:** Alembic
* **Banco de Dados:** PostgreSQL
* **Infraestrutura:** Docker / Docker Compose
* **Testes:** Pytest

---

## 🐘 Escolha do Banco de Dados

A decisão técnica pelo uso do **PostgreSQL** baseou-se em critérios de eficiência operacional e alinhamento com a stack:

* **Sinergia com a Stack:** O PostgreSQL é a referência para aplicações Python com FastAPI e SQLAlchemy, possuindo os drivers mais estáveis e melhor suporte do ORM para operações assíncronas.
* **Facilidade com Docker:** A maturidade da imagem oficial no Docker Hub garante uma configuração de ambiente simples, previsível e idêntica entre desenvolvimento e testes.
* **Adoção de Mercado:** Trata-se de um banco amplamente utilizado por empresas de diversos portes, garantindo que o projeto siga padrões de indústria e possua farta documentação comunitária.
* **Expertise da Equipe:** A familiaridade dos membros do time com a tecnologia permitiu uma curva de aprendizado nula na configuração da infraestrutura, focando o esforço no desenvolvimento das regras de negócio.


---

## 📌 Principais Funcionalidades da API

### 👤 Clientes
* CRUD completo.
* Identificação única por CPF/CNPJ.
* Validação de formato e dígitos verificadores.

### 🚗 Veículos
* Associados a clientes.
* Cadastro via CPF no path.
* Validação de placa (padrão antigo e Mercosul).

### 🧰 Serviços e Peças
* CRUD completo.
* Serviços com preço.
* Peças com controle de estoque.

### 🧾 Ordens de Serviço (OS)
* Criação vinculada a cliente e veículo.
* Inclusão de serviços e peças.
* Orçamento calculado automaticamente.
* **Fluxo de status:** `RECEBIDA` -> `EM_DIAGNOSTICO` -> `AGUARDANDO_APROVACAO` -> `EM_EXECUCAO` -> `FINALIZADA` -> `ENTREGUE`.

### ✅ Aprovação do Orçamento
* Endpoint público.
* Identificação do cliente via CPF.
* Transição automática para `EM_EXECUCAO` e registro do início da execução.

### ⏱️ Métricas
* Monitoramento do tempo médio de execução das OS (baseado no período entre `EM_EXECUCAO` e `FINALIZADA`).

### 🔐 Autenticação
* A maioria dos endpoints é protegida por **JWT**.
* O endpoint de aprovação do orçamento é público, conforme requisito funcional.
* Em testes automatizados, a autenticação é mockada via override de dependência.

