# PRD - LicitAI (Product Requirements Document)

**Objetivo:** SaaS de Inteligência Competitiva para automação de monitoramento de licitações no portal PNCP.

**Foco Técnico:** Oportunidades de TI, Observabilidade e Monitoramento (Zabbix, Splunk, SolarWinds, AppDynamics, Grafana, NOC 24x7).

---

## 1. Funcionalidades Core

### 1.1 Ingestão Automatizada

- **Busca automática diária de novos editais** nas APIs oficiais do governo (PNCP).
- Gatilho focado nas publicações referentes a oportunidades de compra atualizadas do dia de execução.

### 1.2 Filtro Inteligente & OCR

- **Filtro de objetos de compra:** Aplicação de Regex (Expressão Regular) avançada baseada previamente em fluxos testados no n8n.
- **Processamento de PDF:** Captura do documento oficial e extração de seu conteúdo completo para envio ao LLM via OCR nativo, ou fallback via Machine Learning computacional de visão caso o PDF seja convertido como imagem pela prefeitura.

### 1.3 Machine Learning (LLM) & Score

- Extração de dados críticos (Valor, Data da Sessão, Tecnologias citadas implicitamente no edital).
- **Score de Vencibilidade (0-10):** Ranquear oportunidades com base na aderência técnica da empresa a stack buscada (infraestrutura e monitoramento avançado).

### 1.4 Notificações e Engajamento

- **Alertas Instantâneos:** Disparo imediato via Bot no Telegram para a gerência de novos editais "Quentes" (Score > 8).
- **Alertas HTML:** Disparos de E-mail profissionais sumariados.

---

## 2. Visão do Administrativo

O painel deve conter uma área segura (`/admin_dashboard`) restrita ao proprietário para visualização de sucesso do Worker, uso de fallbacks de OCR (que custam mais processamento) e registro de erros na captura para eventual refatoração.
