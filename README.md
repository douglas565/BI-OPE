# BI-OPE

Projeto Power BI (formato **PBIP/TMDL** — Developer Mode) do **Painel OPE** — Iluminação Pública CWB (ENGIE).
Migração do painel HTML/JS original (em `site-referencia/`) para modelo semântico + relatório.

## Como abrir no Power BI Desktop

1. Baixe o repositório como ZIP (`Code` → `Download ZIP`) e extraia.
2. Abra `powerbi/Workshop BI.pbip` no **Power BI Desktop**.
3. Clique em **Atualizar** para carregar os dados:
   - **F_atendimentos** — API Exati `engiecuritiba.exati.com.br` (credenciais embutidas — veja abaixo; o período da consulta é o parâmetro `DATA_INICIO` no M, hoje `01/06/2026`);
   - **D_turnos** — Horários pré-setados (T1/T2/T3, meta 15), editáveis no M;
   - **F_paradas / F_planejamento** — listas do SharePoint ENGIE (exigem login no tenant);
   - **D_Calendario / D_equipes / D_Motivo** — derivadas (não acessam fontes externas).

## Credenciais da API Exati

A senha do usuário `consulta.webservice` está **embutida** na consulta `F_atendimentos` (etapa `Pass`), por decisão do projeto — permite atualizar os dados direto no Desktop sem edição manual.
Recomendações: manter o repositório **privado** e rotacionar a senha periodicamente.

## Estrutura

- `powerbi/` — projeto PBIP (`.pbip` + relatório + modelo semântico em TMDL)
- `site-referencia/` — painel HTML/CSS/JS original (referência funcional)
- `themes/OPE-ENGIE-CWB.json` — tema visual (paleta do painel)
- `docs/regras-ope.md` — regras de cálculo do OPE
- `tests/validate_pbip.py` — validador estático do projeto (`python3 tests/validate_pbip.py`)

## Status (2026-10-02)

- Corrigido o crash de abertura no Desktop (`PFE_TM_RELATIONSHIP_END_COLUMN_INVALID`): `D_Calendario` virou tabela de **importação (M)** — relacionamentos não podem ser criados no cold load contra tabelas calculadas.
- Corrigido o conflito de merge de annotations (`TMDL objects cannot be merged...`): `PBI_ResultType`/`PBI_NavigationStepName` agora indentadas sob as tabelas (antes em coluna 0, eram tratadas como anotações de banco de dados).
- `cultures/pt-BR.tmdl` limpo (sem resíduos de auto date/time / "Variation").
- Performance alinhada ao contrato vigente: **realizados ÷ meta de 15/equipe-dia**; métricas de tempo só como referência.
- Unidades do modelo em **minutos** (paradas e metas). Turno (T1/T2/T3) atribuído na consulta.

## Relatório (abas) — 2026-10-02

Criadas/atualizadas 5 abas no relatório:

1. **Visão Geral OPE** — OPE (gauge) + Disponibilidade/Performance/Qualidade (cartões), Realizados × meta, tendência por data, OPE por equipe, resumo por equipe e segmentadores (período/equipe).
2. **Disponibilidade** — cartões (tempo base/disponível, paradas), tempo disponível × paradas por data, disponibilidade por equipe, paradas por motivo (min) e tabela de paradas registradas.
3. **Performance** — cartões (realizados, meta, equipe-dia), realizados × meta por data/equipe e detalhe por equipe/dia.
4. **Qualidade** — cartões, impossibilidades por data/motivo/equipe e tabela de atendimentos.
5. **Análise por Equipe** — tabela consolidada D/P/Q/OPE por equipe.

- **Paradas:** consulta `F_paradas` lê a lista **"Relatório de paradas CWB"** do site SharePoint *Cidades Inteligentes* (seleção por Id da lista, com fallback por nome). Requer login no tenant ao atualizar.

## Correções 2026-10-02 (pós-teste no Desktop)

- **Medidas DAX:** referências entre medidas estavam com apóstrofo (`['Nome']`) — inválido no DAX e causa dos erros "Missing_References / campos que precisam ser corrigidos". Todas as 11 medidas foram corrigidas para `[Nome]`. Validador agora rejeita esse padrão.
- **Consulta Exati (`F_atendimentos`):** a URL agora é montada com `[Query = [...]]` (encoding garantido dos parâmetros) em vez de concatenar querystring; se a resposta vier sem `PONTOS_ATENDIDOS`, o erro mostra o conteúdo retornado pela API (auto-diagnóstico).

## Pendências
- Recorte de paradas à janela do turno; rateio da meta entre turnos; parâmetros para caminhos/credenciais.
