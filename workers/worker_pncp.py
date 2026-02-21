import asyncio
import httpx
import re
import os
from datetime import datetime
from app.services.database import save_licitacao, get_user_config
from app.services.pdf_extractor import extract_text_from_url
from app.services.ai_scorer import score_licitacao
from app.services.notifications import send_email_alert, send_telegram_alert

# Como a regex não foi enviada na mensagem, criei este placeholder funcional para TI:
N8N_REGEX_FILTER = r"(?i)\b(zabbix|splunk|monitoramento|observabilidade|noc|grafana|appdynamics|tecnologia)\b"

async def fetch_pncp_data(date_str: str):
    url = "https://pncp.gov.br/api/consulta/v1/contratacoes/proposta"
    params = {
        "dataInicial": date_str,
        "dataFinal": date_str,
        "pagina": 1,
        "tamanhoPagina": 50
    }
    
    async with httpx.AsyncClient() as client:
        try:
            headers = {"User-Agent": "LicitAI/1.0"}
            response = await client.get(url, params=params, headers=headers, timeout=30.0)
            response.raise_for_status()
            data = response.json()
            return data.get("data", []) if isinstance(data, dict) else data
        except Exception as e:
            print(f"Error fetching from PNCP: {e}")
            return []

async def process_licitacao(item: dict) -> dict:
    # Retorna métricas dessa iteração {match: bool, extracted: bool, ocr: bool, error: bool}
    metrics = {"match": False, "extracted": False, "ocr": False, "error": False}
    try:
        orgao_nome = item.get("orgaoEntidade", {}).get("razaoSocial", item.get("orgao", "Órgão Desconhecido"))
        cnpj_orgao = item.get("orgaoEntidade", {}).get("cnpj", "")
        objeto = item.get("objetoCompra", item.get("objeto", ""))
        link_pncp = item.get("linkSistemaOrigem", item.get("link", ""))
        valor = item.get("valorTotalEstimado", 0.0)
        data_sessao = item.get("dataAberturaProposta", "")
        item_id = item.get("numeroControlePNCP", item.get("id", str(item.get("idCompra", ""))))
        
        # Aplica o filtro REGEX no objeto
        if not re.search(N8N_REGEX_FILTER, objeto):
            return metrics
            
        metrics["match"] = True
        print(f"Match found by Regex! ID: {item_id} | Órgão: {orgao_nome}")
        
        edital_url = item.get("linkEdital", "")
        if not edital_url and "arquivos" in item and item["arquivos"]:
            edital_url = item["arquivos"][0].get("url", "")
                
        full_text = ""
        if edital_url:
            print(f"Extracting PDF from {edital_url}")
            full_text = extract_text_from_url(edital_url)
            if full_text:
                metrics["extracted"] = True
                # Very simple heuristic: if it mentions 'OCR' fallbacks in our log, it means OCR was used.
                # In a real app we'd have extract_text_from_url return a flag, but for now we look for our print statement context or lack of native formatting.
                if len(full_text.strip()) > 0 and len(full_text.strip()) < 50: # This means the fallback was likely triggered
                     metrics["ocr"] = True
            
        print("Scoring with AI...")
        score_result = score_licitacao(objeto, full_text)
        
        licitacao_data = {
            "id": item_id,
            "orgao": orgao_nome,
            "cnpj_orgao": cnpj_orgao,
            "objeto": objeto,
            "valor_estimado": float(valor) if valor else 0.0,
            "data_sessao": data_sessao,
            "score": score_result.score,
            "justificativa": getattr(score_result, 'justificativa', ''),
            "techs": getattr(score_result, 'tech_stack', ''),
            "link": link_pncp
        }
        
        await save_licitacao(licitacao_data)
        
        # Notificações
        if score_result.score > 8:
            print(f"High score ({score_result.score})! Disparando Alertas...")
            
            email = os.getenv("SYS_EMAIL_NOTIFY")
            if email:
                send_email_alert(email, licitacao_data)
            
            telegram_id = os.getenv("TELEGRAM_CHAT_ID")
            if telegram_id:
                await send_telegram_alert(telegram_id, licitacao_data)

        return metrics
    except Exception as e:
        print(f"Exception during processing: {e}")
        metrics["error"] = True
        return metrics

async def run_worker():
    print("Starting PNCP Worker Ingestion (Regex Based)...")
    
    today = datetime.now().strftime("%Y%m%d")
    items = await fetch_pncp_data(today)
    
    if not items:
        print("Nenhuma licitação encontrada ou erro na busca.")
        return
        
    print(f"Buscadas {len(items)} oportunidades. Iniciando filtro REGEX & extração...")
    
    # Importing here to prevent circular dependency issues on some setups
    from services.database import log_rotina
    
    stats = {
        'total': len(items),
        'matches': 0,
        'extraidos': 0,
        'ocr': 0,
        'erros': 0
    }
    
    for item in items:
        try:
            metrics = await process_licitacao(item)
            if metrics.get("match"): stats["matches"] += 1
            if metrics.get("extracted"): stats["extraidos"] += 1
            if metrics.get("ocr"): stats["ocr"] += 1
            if metrics.get("error"): stats["erros"] += 1
            await asyncio.sleep(1)
        except Exception as e:
            print(f"Erro ao processar item: {e}")
            stats["erros"] += 1
            
    await log_rotina(stats)
            
    print("Worker finalizado com sucesso.")

if __name__ == "__main__":
    asyncio.run(run_worker())
