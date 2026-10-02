# Regras OPE

Contrato vigente (alinhado ao painel OPE v3 e ao modelo TMDL):

1. **Disponibilidade**: (Tempo Base - Paradas) / Tempo Base. Tempo Base = META DISPONIBILIDADE do turno (bruto - mobilizacao - desmobilizacao - deslocamento - intervalo), somado por equipe-dia-turno. Paradas em minutos (pendente: recorte a janela do turno).
2. **Performance**: realizados / meta de producao. Meta = **15 chamados por equipe/dia** (rateada entre turnos quando ha mais de um turno no dia). **Sem componente de tempo** - 15 de 15 = 100%. (Leitura por tempo - meta 0:23 x validos / tempo disponivel - permanece apenas como metrica de referencia, fora do OPE.)
3. **Qualidade**: validos / realizados, com impossibilidade = status diferente de "Atendido" **e** contendo "IMP" (texto normalizado).
4. **OPE**: Disponibilidade x Performance x Qualidade (sem limite de 100% por padrao; medidas limitadas disponiveis).
5. Equipes CCO sao excluidas de todos os calculos.
6. Data operacional: atendimentos ate 06:30 pertencem ao dia anterior (turno da madrugada).
7. Turno: T3 = 22:00->06:00 (madrugada conta no dia anterior); horarios fora das janelas (06:01-07:29) nao entram nos indicadores.
