import os
import resend
from telegram import Bot

def send_email_alert(recipient: str, licitacao_data: dict):
    api_key = os.getenv("RESEND_API_KEY")
    if not api_key:
        print("RESEND_API_KEY not configured. Skipping email.")
        return
        
    resend.api_key = api_key
        
    html_content = f"""
    <h2>🔥 Nova Oportunidade Quente Encontrada!</h2>
    <p><strong>Órgão:</strong> {licitacao_data.get('orgao')}</p>
    <p><strong>Objeto:</strong> {licitacao_data.get('objeto')}</p>
    <p><strong>Valor Estimado:</strong> R$ {licitacao_data.get('valor_estimado', 0.0)}</p>
    <p><strong>Data da Sessão:</strong> {licitacao_data.get('data_sessao')}</p>
    <p><strong>Score de Vencibilidade:</strong> {licitacao_data.get('score')}/10</p>
    <p><strong>Tech Stack Identificada:</strong> {licitacao_data.get('tech_stack')}</p>
    <p><a href="{licitacao_data.get('link')}">Ver Licitação no PNCP</a></p>
    """
    
    try:
        r = resend.Emails.send({
          "sender": "LicitAI <onboarding@resend.dev>",
          "to": recipient,
          "subject": f"[{licitacao_data.get('score')}/10] Oportunidade: {licitacao_data.get('orgao')}",
          "html": html_content
        })
        print(f"Email sent successfully: {r}")
    except Exception as e:
        print(f"Error sending email: {e}")

async def send_telegram_alert(chat_id: str, licitacao_data: dict):
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token or not chat_id:
        print("TELEGRAM_BOT_TOKEN or chat_id not configured. Skipping Telegram alert.")
        return
        
    bot = Bot(token=token)
    message = (
        f"🔥 *Nova Oportunidade Quente (Score {licitacao_data.get('score')}/10)*\n\n"
        f"🏢 *Órgão*: {licitacao_data.get('orgao')}\n"
        f"📝 *Objeto*: {licitacao_data.get('objeto')}\n"
        f"💰 *Valor*: R$ {licitacao_data.get('valor_estimado', 0.0)}\n"
        f"📅 *Data*: {licitacao_data.get('data_sessao')}\n"
        f"💻 *Tech*: {licitacao_data.get('tech_stack')}\n\n"
        f"🔗 [Acessar PNCP]({licitacao_data.get('link')})"
    )
    
    try:
        await bot.send_message(chat_id=chat_id, text=message, parse_mode="Markdown")
        print("Telegram alert sent successfully.")
    except Exception as e:
        print(f"Error sending Telegram alert: {e}")
