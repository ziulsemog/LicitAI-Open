# TECH SPECS - LicitAI

Arquitetura e especificações técnicas oficiais do LicitAI SaaS baseadas em sua construção.

## 1. Stack Tecnológica

- **Backend:** Python 3.11+ com framework **FastAPI**.
- **Banco de Dados:** **Turso (libSQL)** para persistência de dados distribuída na borda (edge) garantindo custo zero inicial e integração HTTP Client-less (via `libsql_client`).
- **Autenticação:** **Clerk** (JWT). Apenas via backend; interceptação e validação via Public Keys do Clerk (`.well-known/jwks.json`). Proteção de rotas da aplicação via Header `Bearer`.
- **E-mail:** **Resend** (SDK Python) para disparos transacionais de oportunidades Quentes.
- **Mensageria:** **Telegram Bot API** (`python-telegram-bot`) usando Markdown para legibilidade.
- **Inteligência Artificial:** **Gemini 1.5 Flash** empacotado via **LangChain** otimizado para extração de outputs tipados com `Pydantic` via _Structured Output_ com consumo inteligente e barato de requests/tokens.

## 2. Processamento Híbrido de PDF

O Motor de PDF é programado para economizar RAM em ambientes Serverless:

1.  **Primário:** `PyMuPDF` (`fitz`) processa os bytes extraídos da URL focando em renderizar textos embarcados do PostScript. Se o retorno for menor que 50 caracteres (típica folha raspada/scanneada):
2.  **Fallback (OCR):** `EasyOCR` faz leitura das imagens bufferizadas em memória utilizando Optical Character Recognition para salvar o preenchimento sem perder oportunidades ricas. (Tesseract mapeador incluído no pipeline de CI/CD).

## 3. Infraestrutura & Cloud

- **Deploy Host:** Vercel.
- **Cron Jobs:** `vercel.json` mapeado para a rota `/api/cron/worker` da API (index.py mascarado para compatibilidade), invocando assincronamente a esteira diariamente.
- **Integração Contínua:** GitHub Actions monitora a branch `main` realizando o `Pytest` da aplicação emulando credenciais fictícias de Cloud para mitigar deploys instáveis no Turso.

## 4. Banco de Dados / Entidades Chaves

```sql
CREATE TABLE licitacoes (
    id TEXT PRIMARY KEY,
    orgao TEXT,
    cnpj_orgao TEXT,
    objeto TEXT,
    valor_estimado REAL,
    data_sessao TEXT,
    score_vencibilidade INTEGER,
    justificativa_ia TEXT,
    tecnologias_detectadas TEXT,
    link_edital TEXT,
    status TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE rotinas_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    data_execucao DATETIME DEFAULT CURRENT_TIMESTAMP,
    total_encontrado INTEGER,
    matches_regex INTEGER,
    pdf_extraidos INTEGER,
    pdf_ocr_usado INTEGER,
    erros INTEGER
);
```
