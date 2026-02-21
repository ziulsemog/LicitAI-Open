import os
import libsql_client
from dotenv import load_dotenv

load_dotenv()

# Configurações de conexão com o Turso
url = os.getenv("TURSO_DATABASE_URL")
auth_token = os.getenv("TURSO_AUTH_TOKEN")

def get_db_client():
    """Retorna um cliente de conexão com o banco Turso."""
    return libsql_client.create_client(url, auth_token=auth_token)

async def save_licitacao(data):
    """Insere ou atualiza uma licitação no banco de dados."""
    async with get_db_client() as client:
        # Create tables on first usage if they don't exist
        await client.execute("""
            CREATE TABLE IF NOT EXISTS licitacoes (
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
            )
        """)
        await client.execute("""
            CREATE TABLE IF NOT EXISTS rotinas_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                data_execucao DATETIME DEFAULT CURRENT_TIMESTAMP,
                total_encontrado INTEGER,
                matches_regex INTEGER,
                pdf_extraidos INTEGER,
                pdf_ocr_usado INTEGER,
                erros INTEGER
            )
        """)
        
        query = """
        INSERT INTO licitacoes (
            id, orgao, cnpj_orgao, objeto, valor_estimado, 
            data_sessao, score_vencibilidade, justificativa_ia, 
            tecnologias_detectadas, link_edital, status
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(id) DO UPDATE SET
            status = excluded.status,
            score_vencibilidade = excluded.score_vencibilidade;
        """
        params = [
            data['id'], data['orgao'], data.get('cnpj_orgao'), 
            data['objeto'], data.get('valor_estimado'), data.get('data_sessao'),
            data.get('score'), data.get('justificativa'),
            data.get('techs'), data.get('link'), 'novo'
        ]
        await client.execute(query, params)

async def log_rotina(stats: dict):
    """Registra uma execução do worker no banco de dados."""
    async with get_db_client() as client:
        query = """
        INSERT INTO rotinas_log (
            total_encontrado, matches_regex, pdf_extraidos, pdf_ocr_usado, erros
        ) VALUES (?, ?, ?, ?, ?)
        """
        params = [
            stats.get('total', 0),
            stats.get('matches', 0),
            stats.get('extraidos', 0),
            stats.get('ocr', 0),
            stats.get('erros', 0)
        ]
        await client.execute(query, params)

async def get_admin_stats():
    """Busca as estatísticas das últimas 24h para o dashboard."""
    async with get_db_client() as client:
        # Pega métricas sumariadas das últimas rotinas do dia atual
        rotinas_res = await client.execute("""
            SELECT 
                SUM(total_encontrado) as buscas_diarias,
                SUM(pdf_ocr_usado) as ocr_status,
                SUM(erros) as erros
            FROM rotinas_log
            WHERE data_execucao >= datetime('now', '-1 day')
        """)
        
        # Pega as últimas 5 licitações quentes para visualização (Score > 8)
        licitacoes_res = await client.execute("""
            SELECT id, orgao, score_vencibilidade, tecnologias_detectadas, created_at 
            FROM licitacoes 
            WHERE score_vencibilidade > 8
            ORDER BY created_at DESC 
            LIMIT 5
        """)
        
        row = rotinas_res.rows[0] if rotinas_res.rows else None
        stats = {
            "buscas_diarias": row[0] if row and row[0] is not None else 0,
            "ocr_status": row[1] if row and row[1] is not None else 0,
            "alertas_erro": row[2] if row and row[2] is not None else 0,
            "recent_hot": [
                {
                    "id": l[0], 
                    "orgao": l[1], 
                    "score": l[2], 
                    "techs": l[3], 
                    "date": l[4]
                } for l in licitacoes_res.rows
            ] if licitacoes_res.rows else []
        }
        return stats

async def get_user_config(user_id):
    """Busca as configurações de filtros do usuário (Clerk ID)."""
    async with get_db_client() as client:
        result = await client.execute(
            "SELECT * FROM configs WHERE user_id = ?", [user_id]
        )
        return result.rows[0] if result.rows else None
