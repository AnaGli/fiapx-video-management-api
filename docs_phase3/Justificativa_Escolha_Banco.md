# Justificativa da Escolha do Banco de Dados e Modelagem Relacional

## Visão Geral

O sistema foi desenvolvido para gerenciar operações de oficina mecânica, incluindo:

- clientes
- veículos
- ordens de serviço
- itens de ordem
- peças
- movimentações de estoque

A aplicação possui forte dependência de relacionamentos entre entidades e necessidade de consistência transacional.

Diante desses requisitos, foi adotado:

```text
PostgreSQL executando no Amazon RDS
```

---

# Justificativa da Escolha do Banco de Dados

## 1. Modelo fortemente relacional

O domínio da aplicação possui entidades altamente conectadas:

- Um cliente pode possuir múltiplos veículos
- Um veículo pode possuir múltiplas ordens de serviço
- Uma ordem possui múltiplos itens
- Itens podem representar serviços ou peças
- Peças possuem movimentações de estoque

Esse cenário exige:
- integridade referencial
- joins eficientes
- constraints relacionais
- consistência transacional

O PostgreSQL possui excelente aderência para esse tipo de domínio.

---

## 2. Consistência transacional (ACID)

O fluxo de ordens de serviço exige operações consistentes.

Exemplo:
- criação ordem
- inclusão itens
- movimentação estoque
- aprovação ordem

Essas operações precisam ocorrer atomicamente.

O PostgreSQL oferece:
- transações ACID
- rollback
- controle concorrência
- consistência forte

---

## 3. Compatibilidade com FastAPI e SQLAlchemy

A stack da aplicação utiliza:
- FastAPI
- SQLAlchemy
- Alembic

O PostgreSQL possui integração madura com:
- ORM SQLAlchemy
- migrations Alembic
- drivers Python robustos

---

## 4. Serviço gerenciado no Amazon RDS

A utilização do Amazon RDS reduz o overhead operacional.

Benefícios:
- backups automáticos
- failover
- monitoramento
- alta disponibilidade
- patching gerenciado

---

# Modelo Entidade Relacionamento (ER)

## Estrutura Geral

O modelo foi estruturado de forma normalizada para:
- evitar redundância
- garantir integridade
- facilitar manutenção
- suportar escalabilidade futura

---

# Entidades Principais

| Entidade | Objetivo |
|---|---|
| clients | Cadastro clientes |
| vehicles | Veículos clientes |
| service_orders | Ordens serviço |
| service_order_items | Itens ordem |
| parts | Catálogo peças |
| stock_movements | Controle estoque |

---

# Diagrama ER

## Relacionamentos identificados

```text
clients (1) -------- (N) vehicles

clients (1) -------- (N) service_orders

vehicles (1) ------- (N) service_orders

service_orders (1) - (N) service_order_items

parts (1) ---------- (N) stock_movements
```

---

# Explicação dos Relacionamentos

## 1. Cliente → Veículos

Relacionamento:
```text
1:N
```

Um cliente pode possuir:
- múltiplos veículos

Cada veículo pertence a:
- apenas um cliente

Relacionamento implementado via:

```text
vehicles.client_id
```

---

## 2. Cliente → Ordens de Serviço

Relacionamento:
```text
1:N
```

Um cliente pode possuir:
- múltiplas ordens de serviço

Cada ordem pertence a:
- apenas um cliente

Relacionamento implementado via:

```text
service_orders.client_id
```

---

## 3. Veículo → Ordens de Serviço

Relacionamento:
```text
1:N
```

Um veículo pode possuir:
- várias ordens

Cada ordem pertence a:
- apenas um veículo

Relacionamento implementado via:

```text
service_orders.vehicle_id
```

---

## 4. Ordem de Serviço → Itens

Relacionamento:
```text
1:N
```

Uma ordem pode conter:
- múltiplos itens

Os itens podem representar:
- serviços
- peças

Relacionamento implementado via:

```text
service_order_items.service_order_id
```

---

## 5. Peças → Movimentações Estoque

Relacionamento:
```text
1:N
```

Uma peça pode possuir:
- múltiplas movimentações

Cada movimentação pertence a:
- uma única peça

Relacionamento implementado via:

```text
stock_movements.part_id
```

---

# Ajustes Realizados na Modelagem

## 1. Inclusão de Soft Delete

Na tabela:

```text
clients
```

foi adicionada:

```text
is_active BOOLEAN
```

Objetivo:
- evitar deleção física
- preservar histórico
- permitir desativação lógica

---

## 2. Separação entre Ordem e Itens

Foi adotada separação:

| Tabela | Responsabilidade |
|---|---|
| service_orders | Cabeçalho ordem |
| service_order_items | Itens detalhados |

Benefícios:
- normalização
- flexibilidade
- expansão futura

---

## 3. Controle de Estoque Isolado

Movimentações foram separadas em:

```text
stock_movements
```

permitindo:
- auditoria
- histórico movimentações
- rastreabilidade estoque

---

# Benefícios da Modelagem Relacional

## Integridade Referencial

Garantida através de:
- foreign keys
- constraints
- relacionamentos explícitos

---

## Facilidade de Consulta

O modelo favorece:
- joins eficientes
- consultas analíticas
- relatórios operacionais

---

## Consistência

As transações garantem:
- integridade estoque
- consistência ordens
- confiabilidade dados

---

# Considerações de Escalabilidade

Embora relacional, o modelo foi preparado para:
- evolução futura
- separação domínios
- microsserviços

Além disso:
- Kubernetes permite escalabilidade horizontal aplicação
- PostgreSQL RDS suporta crescimento vertical e read replicas

---

# Conclusão

A escolha do PostgreSQL foi motivada por:

- forte aderência relacional
- consistência transacional
- integração madura com FastAPI
- suporte robusto AWS

A modelagem relacional adotada oferece:
- integridade
- rastreabilidade
- escalabilidade futura
- facilidade operacional

O resultado é uma arquitetura consistente, resiliente e preparada para evolução contínua.