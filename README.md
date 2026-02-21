# 🚀 LicitAI SaaS

<div align="center">
  <img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white" />
  <img src="https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white" />
  <img src="https://img.shields.io/badge/Turso-000000?style=for-the-badge&logo=turso&logoColor=white" />
  <img src="https://img.shields.io/badge/Clerk-6C47FF?style=for-the-badge&logo=clerk&logoColor=white" />
  <img src="https://img.shields.io/badge/Vercel-000000?style=for-the-badge&logo=vercel&logoColor=white" />
  <img src="https://img.shields.io/badge/Gemini_AI-4285F4?style=for-the-badge&logo=google&logoColor=white" />
</div>

<br />

SaaS de Inteligência Competitiva para automação e monitoramento inteligente de licitações no portal PNCP. Focado em filtrar oportunidades Quentes de Tecnologia (TI), Observabilidade, e Monitoramento utilizando Filtros Regex precisos e ranqueamento via Inteligência Artificial.

---

## 🏗 Arquitetura Visual

O funcionamento do **LicitAI** acontece de forma autônoma (Serverless) diariamente às 8h da manhã. O fluxo principal engloba:

1. **PNCP API:** Consumo massivo de editais publicados no dia.
2. **Python Worker:** Filtro Regex Inteligente (ex: Zabbix, Splunk, AppDynamics). Download de editais PDFs e uso de OCR Nativo (PyMuPDF) ou OCR fallback (EasyOCR).
3. **Gemini AI:** Motor cognitivo que julga o edital baixado e atribui um "Score de Vencibilidade" de 0 a 10 e explica a aderência.
4. **Turso DB (libSQL):** Guardião do histórico distribuído na borda, rápido e de custo zero para inicialização.
5. **Notificações:** Alertas diretos no **Telegram** via Bot e disparo de e-mail HTML via **Resend**.
6. **Dashboard & Auth (Clerk):** Painel web `/admin_dashboard` exclusivo e seguro que monitora o desempenho do banco através de autenticação por tokens JWT (Clerk).

---

## 📂 Estrutura do GitHub

O repositório é particionado para garantir organização e escala:

- `/.github/workflows/`: Pipelines de CI/CD para automação de testes (Pytest) on-push.
- `/app/`: O core absoluto e as rotas REST do nosso backend **FastAPI**, incluindo os middlewares seguros (Clerk).
- `/app/services`: Operações da aplicação, conexão Turso, parser PDF e integrações (Resend/Telegram).
- `/workers/`: Scripts autônomos (`worker_pncp.py`) que rodam em background ou via cron do Vercel.
- `/docs/`: Documentações como [Product Requirements Document (PRD)](./docs/PRD.md) ou Especificações Técnicas.
- `/tests/`: Testes automatizados da aplicação.

---

## 🚀 Guia de Instalação (Local)

1. **Clone este Repositório**

   ```bash
   git clone https://github.com/SeuUser/LicitAI.git
   cd LicitAI
   ```

2. **Crie e Ative um Ambiente Virtual**

   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Instale as Dependências**

   ```bash
   pip install -r requirements.txt
   ```

4. **Variáveis de Ambiente**  
   Preencha na raiz do diretório o arquivo de variáveis baseado no template original.

   ```bash
   cp .env.example .env
   # Edite as chaves do Turso, Gemini, Telegram, Clerk etc.
   ```

5. **Execute a API Localmente**
   ```bash
   uvicorn app.api:app --reload
   ```
   > Visite: `http://127.0.0.1:8000/admin_dashboard`

## ☁️ Deploy via Vercel

Crie ou conecte um projeto Vercel nesta base de código, configure suas Variáveis de Ambiente e pronto!

[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new)

---

## 🤝 Como Contribuir

1. Faça um Fork do projeto.
2. Crie uma Branch para as suas alterções (`git checkout -b feature/minhanovafeature`).
3. Commit suas mudanças (`git commit -am 'Add some feature'`).
4. Push para a branch (`git push origin feature/minhanovafeature`).
5. Abra um novo Pull Request.

---

Feito com ☕ e IA para potencializar empresas de tecnologia em licitações públicas!
