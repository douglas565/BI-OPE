# BI-OPE

Projeto Power BI (formato **PBIP/TMDL** — Developer Mode) do **Painel OPE** — Iluminação Pública CWB (ENGIE).
Migração do painel HTML/JS original (em `site-referencia/`) para modelo semântico + relatório.

## Como abrir no Power BI Desktop

1. Baixe o repositório como ZIP (`Code` → `Download ZIP`) e extraia.
2. Abra `powerbi/Workshop BI.pbip` no **Power BI Desktop** (release agosto/2026 ou superior).
3. Na primeira abertura o modelo carrega **sem dados** (importação). Clique em **Atualizar** para buscar os dados:
   - **F_atendimentos** — API Exati `engiecuritiba.exati.com.br` (requer senha, veja abaixo; o período da consulta é o parâmetro `DATA_INICIO` no M, hoje `01/06/2026`);
   - **D_turnos** — Horários pré-setados (T1/T2/T3, meta 15), editáveis no M;
   - **F_paradas / F_planejamento** — listas do SharePoint ENGIE (exigem login no tenant);
   - **D_Calendario / D_equipes / D_Motivo** — derivadas (não acessam fontes externas).

## Senha da API Exati (necessária para atualizar os atendimentos)

Por segurança, a senha **não** está versionada — ela aparece como `#REPLACESECRET#` na consulta `F_atendimentos`.
Antes de atualizar: `Página Inicial` → `Transformar dados` → consulta **F_atendimentos** → etapa `Pass` →
substituir `#REPLACESECRET#` pela senha do usuário `consulta.webservice` → `Fechar e Aplicar`.

> Recomendação: rotacionar essa senha (ela aparece em commits antigos deste repositório) e, se possível, tornar o repositório privado.

## Estrutura

- `powerbi/` — projeto PBIP (`.pbip` + relatório + modelo semântico em TMDL)
- `site-referencia/` — painel HTML/CSS/JS original (referência funcional)
- `themes/OPE-ENGIE-CWB.json` — tema visual (paleta do painel)
- `docs/regras-ope.md` — regras de cálculo do OPE
- `tests/validate_pbip.py` — validador estático do projeto (`python3 tests/validate_pbip.py`)

## Status (2026-10-02)

- Corrigido o crash de abertura no Desktop (`PFE_TM_RELATIONSHIP_END_COLUMN_INVALID`): `D_Calendario` virou tabela de **importação (M)** — relacionamentos não podem ser criados no cold load contra tabelas calculadas.
- `cultures/pt-BR.tmdl` limpo (sem resíduos de auto date/time / "Variation").
- Performance alinhada ao contrato vigente: **realizados ÷ meta de 15/equipe-dia**; métricas de tempo só como referência.
- Unidades do modelo em **minutos** (paradas e metas).
- Turno (T1/T2/T3) atribuído na consulta conforme as janelas do painel.
- Pendente: páginas completas do relatório; recorte de paradas à janela do turno; rateio da meta entre turnos; parâmetros para caminhos/credenciais.
