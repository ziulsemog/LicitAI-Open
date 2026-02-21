import os
from langchain_google_genai import ChatGoogleGenerativeAI
from pydantic import BaseModel, Field

class LicitacaoScore(BaseModel):
    score: int = Field(description="Score de Vencibilidade de 0 a 10", ge=0, le=10)
    tech_stack: str = Field(description="Principais tecnologias ou requisitos identificados (ex: Zabbix, Splunk, NOC 24x7)")
    justificativa: str = Field(description="Breve justificativa para a nota dada baseada na aderência a TI, Monitoramento, Observabilidade, etc.")

def score_licitacao(objeto: str, full_text: str = "") -> LicitacaoScore:
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("GEMINI_API_KEY is not set.")
        return LicitacaoScore(score=0, tech_stack="", justificativa="Erro: API Key não configurada")
        
    llm = ChatGoogleGenerativeAI(
        model="gemini-1.5-flash",
        google_api_key=api_key,
        temperature=0.0
    )
    
    # Use Structured Output
    structured_llm = llm.with_structured_output(LicitacaoScore)
    
    prompt = f"""
    Analise a seguinte oportunidade de licitação (SaaS de Inteligência Competitiva).
    O foco técnico procurado é: Oportunidades de TI, Observabilidade e Monitoramento (Zabbix, Splunk, SolarWinds, AppDynamics, Grafana, NOC 24x7).
    
    Dê um 'Score de Vencibilidade' de 0 a 10 para esta oportunidade.
    - 0 a 3: Nenhuma relação com TI ou infraestrutura/monitoramento.
    - 4 a 6: Contém itens de TI gerais, mas sem foco explícito em observabilidade/monitoramento.
    - 7 a 10: Forte aderência a Monitoramento, Observabilidade, ou ferramentas específicas citadas.
    
    Objeto da Licitação:
    {objeto}
    
    Trecho do Edital (se disponível):
    {full_text[:3000]} # Limitando p/ economizar tokens
    """
    
    try:
        result = structured_llm.invoke(prompt)
        return result
    except Exception as e:
        print(f"Error during AI scoring: {e}")
        return LicitacaoScore(score=0, tech_stack="", justificativa=f"Erro na IA: {str(e)}")
