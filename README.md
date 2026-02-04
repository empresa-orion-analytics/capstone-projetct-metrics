# 📊 Capstone Project – Metrics Platform

![Arquitetura da Plataforma](Docs/arquitetura.png)

Este repositório contém a implementação de uma **plataforma de dados analíticos** baseada em arquitetura *Lakehouse*, com separação clara entre **ingestão, processamento, publicação e consumo de dados**.

O objetivo do projeto é demonstrar, de ponta a ponta, como dados brutos podem ser transformados em **informação confiável e pronta para consumo por ferramentas de BI**, seguindo boas práticas de engenharia de dados.

---

## 🧠 Visão Geral da Arquitetura

Este projeto simula o funcionamento de uma **empresa de dados especializada em Analytics de Redes Sociais**, responsável por coletar, processar e disponibilizar métricas de performance de vídeos e conteúdos digitais para áreas de negócio e BI.

A arquitetura foi desenhada para ser:
- Escalável
- Reprocessável
- Fácil de operar
- Clara para públicos técnicos e executivos

Fluxo resumido:

**Ingestão → Bronze → Silver → Gold → Publicação Analítica → Visualização**

A **camada Gold no S3** é a *fonte da verdade analítica*. O banco relacional é utilizado exclusivamente como **camada de serving**.

---

## 🏗️ Componentes da Arquitetura

### 1. Ingestão de Dados
- **Fonte**: Faker (dados sintéticos para simulação)
- **Frequência**: 2x ao dia (08h e 20h)
- **Objetivo**: Gerar dados brutos para simular eventos/transações

Os dados são ingeridos sem transformação e armazenados na camada Bronze.

---

### 2. Processamento de Dados – Databricks / Spark

O processamento segue o padrão **Medallion Architecture**:

#### 🥉 Bronze
- Formato: JSON
- Armazenamento: Amazon S3
- Características:
  - Dados brutos
  - Sem tratamento
  - Histórico completo

#### 🥈 Silver
- Exemplo real neste projeto:
  - `silver_criacao_s3.csv`

Nesta camada, os dados representam **eventos de criação/publicação de conteúdos**, já tratados e padronizados para análises posteriores.
- Formato: Parquet
- Armazenamento: Amazon S3
- Características:
  - Dados limpos e padronizados
  - Tipos corretos
  - Prontos para agregações

#### 🥇 Gold
- Exemplos reais neste projeto:
  - `gold_video_views_dia_rede_social.csv`
  - `gold_video_views_dia_faculdade.csv`

A camada Gold consolida **métricas analíticas de redes sociais**, agregadas por dia, rede social e instituição, prontas para consumo por BI.
- Formato: CSV
- Armazenamento: Amazon S3
- Características:
  - Dados agregados
  - Métricas de negócio
  - Prontos para consumo analítico

⏰ **Janela de processamento**:
- Bronze → Silver: 08h e 20h
- Silver → Gold: 22h

---

### 3. Publicação de Dados Analíticos

Responsável por disponibilizar os dados da **camada Gold** para consumo por ferramentas externas.

- **Tecnologia**: AWS Fargate
- **Orquestração**: Amazon EventBridge
- **Horário**: 23h

Função do processo:
- Ler dados da Gold no S3
- Carregar dados no banco analítico
- Não realiza transformações de negócio

Esse processo é chamado de:
> **Publicação de Dados Analíticos**

---

### 4. Banco Analítico

- **Tecnologia**: PostgreSQL (Amazon RDS)
- **Função**: Serving layer
- **Características**:
  - Apenas leitura (BI / Apps)
  - Dados derivados da Gold
  - Pode ser recriado a qualquer momento

O banco **não é fonte da verdade**.

---

### 5. Visualização de Dados

Ferramentas de consumo:
- **Power BI**
- **Streamlit**

Essas ferramentas acessam exclusivamente o banco analítico, garantindo:
- Performance
- Segurança
- Simplicidade de acesso

---

## 📦 Estrutura do Repositório (exemplo)

```
capstone-projetct-metrics/
├── Docs/
│   ├── arquitetura.png
│   └── ArquiteturaProjectCapstone.excalidraw
|
├── Script/
│   └── Script_S3_to_RDS_Postegres.py
|
├── Script_DDL/
|   ├── gold_video_views_dia_faculdade.sql
│   └── gold_video_views_dia_rede_social.sql
│
├── Notebook's/
├────── Bronze
│       └── bronze-faker-ingestao-s3.ipynb
├────── Silver
|       └── silver-criacao-s3.ipynb
├────── Gold
|       ├── gold_video_views_dia_faculdade.ipynb
|       └── gold_video_views_dia_rede_social.ipynb
|
├── Pipiline_Jobs_Databricks
|   ├── Bronze_Silver.yaml
│   └── Gold.yaml
│
├── terraform/
│   └── terraform_rds_postgres.tf
│
├── .env.example
├── README.md
└── requirements.txt
```

> ⚠️ A estrutura pode variar conforme evolução do projeto.

---

## 🚀 Como Executar (Visão Geral)

1. Executar ingestão de dados (Faker)
2. Processar dados no Databricks (Bronze → Silver → Gold)
3. Aguardar fechamento da Gold
4. Executar job de publicação (Fargate)
5. Consumir dados via Power BI ou Streamlit

---

## 🎯 Objetivos do Projeto

- Simular o funcionamento de uma **empresa de Analytics focada em Redes Sociais**
- Demonstrar como métricas de vídeos e engajamento podem ser tratadas e disponibilizadas
- Aplicar boas práticas de Lakehouse (Bronze / Silver / Gold)
- Separar claramente processamento analítico e serving
- Facilitar consumo por ferramentas de BI
- Servir como base para evoluções futuras (incremental, CDC, near real-time)

- Demonstrar arquitetura moderna de dados
- Aplicar boas práticas de Lakehouse
- Separar claramente processamento e serving
- Facilitar consumo analítico
- Servir como base para evoluções futuras (incremental, CDC, near real-time)

---

## 🔮 Próximos Passos (Evoluções Naturais)

- Carga incremental na publicação
- Upsert no banco analítico
- Controle de SLA por camada
- Observabilidade (logs e métricas)
- CI/CD para pipelines

---

## 👥 Público-Alvo

- Engenheiros de Dados
- Analistas de Dados
- Arquitetos de Dados
- Times de BI
- Stakeholders técnicos e de negócio

---

## 📌 Observação Final

Este projeto foi construído com foco em **clareza arquitetural**, **boas práticas** e **facilidade de explicação**, podendo ser utilizado como:
- Capstone project
- Prova de conceito
- Referência interna de arquitetura

---

**Autor**: Orion Analytics  
**Projeto**: Capstone Metrics Platform

