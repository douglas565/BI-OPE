import re

with open("powerbi/Workshop BI.SemanticModel/definition/tables/F_atendimentos.tmdl", "r", encoding="utf-8") as f:
    tmdl = f.read()

# Make sure we don't duplicate
if 'ChaveEquipeDiaTurno' not in tmdl:
    m_script_pattern = re.compile(r'(source = ```\n\s*let\n)(.*?)\n(\s*in\n\s*)(.*?)(\s*```)', re.DOTALL)
    match = m_script_pattern.search(tmdl)
    if match:
        prefix = match.group(1)
        body = match.group(2)
        in_kw = match.group(3)
        last_step = match.group(4)
        suffix = match.group(5)
        
        # New M steps for 4.1 to 4.5
        new_steps = f""",
            DataOperacional = Table.AddColumn({last_step}, "DataOperacional", each if Time.From([DATA_HORA_INICIO_ATENDIMENTO]) <= #time(6, 30, 0) then Date.AddDays(Date.From([DATA_HORA_INICIO_ATENDIMENTO]), -1) else Date.From([DATA_HORA_INICIO_ATENDIMENTO]), type date),
            EquipeNormalizada = Table.AddColumn(DataOperacional, "EquipeNormalizada", each Text.Trim(Text.Replace([DESC_EQUIPE], " | ENGIE", "")), type text),
            EhEquipeCampo = Table.AddColumn(EquipeNormalizada, "EhEquipeCampo", each not Text.Contains([EquipeNormalizada], "CCO", Combiner.OrdinalIgnoreCase), type logical),
            DuracaoExecucaoMin = Table.AddColumn(EhEquipeCampo, "DuracaoExecucaoMin", each if [DATA_HORA_CONCLUSAO_ATENDIMENTO] <> null and [DATA_HORA_CONCLUSAO_ATENDIMENTO] >= [DATA_HORA_INICIO_ATENDIMENTO] then Duration.TotalMinutes([DATA_HORA_CONCLUSAO_ATENDIMENTO] - [DATA_HORA_INICIO_ATENDIMENTO]) else null, type number),
            ExtraTurnoTemp = Table.AddColumn(DuracaoExecucaoMin, "TurnoTemp", each "T1", type text),
            ChaveEquipeDiaTurno = Table.AddColumn(ExtraTurnoTemp, "ChaveEquipeDiaTurno", each [EquipeNormalizada] & "|" & Date.ToText([DataOperacional], "yyyy-MM-dd") & "|" & [TurnoTemp], type text)"""
        
        new_body = body + new_steps
        new_last_step = "ChaveEquipeDiaTurno"
        
        updated = tmdl[:match.start()] + prefix + new_body + in_kw + new_last_step + suffix + tmdl[match.end():]
        
        with open("powerbi/Workshop BI.SemanticModel/definition/tables/F_atendimentos.tmdl", "w", encoding="utf-8") as f:
            f.write(updated)
        print("Patched F_atendimentos M Script successfully.")
    else:
        print("Could not match M script block.")
