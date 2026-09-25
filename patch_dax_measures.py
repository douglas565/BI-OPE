with open("powerbi/Workshop BI.SemanticModel/definition/tables/F_atendimentos.tmdl", "r", encoding="utf-8") as f:
    tmdl = f.read()

new_measures = """
	measure Realizados = CALCULATE( DISTINCTCOUNT(F_atendimentos[ID_ATENDIMENTO_PS]), F_atendimentos[EhEquipeCampo] = TRUE() )
		formatString: 0
		lineageTag: m1

	measure Impossibilidades = CALCULATE([Realizados], D_Motivo[EhImpossibilidade] = TRUE())
		formatString: 0
		lineageTag: m2

	measure Válidos = MAX(0, [Realizados] - [Impossibilidades])
		formatString: 0
		lineageTag: m3

	measure 'Tempo Base Min' = SUMX( VALUES(F_atendimentos[ChaveEquipeDiaTurno]), CALCULATE(MAX(D_turnos[META DISPONIBILIDADE])) )
		formatString: 0
		lineageTag: m4

	measure 'Paradas Min' = SUM(F_paradas[Tempo de parada])
		formatString: 0
		lineageTag: m5

	measure 'Tempo Disponível Min' = MAX(0, [Tempo Base Min] - [Paradas Min])
		formatString: 0
		lineageTag: m6

	measure 'Disponibilidade %' = DIVIDE([Tempo Disponível Min], [Tempo Base Min])
		formatString: 0.0%
		lineageTag: m7

	measure 'Meta Tempo Min' = COALESCE(MAX(D_turnos[META PRODUTIVIDADE (hh)]), 23)
		formatString: 0
		lineageTag: m8

	measure 'Tempo Necessário Min' = [Meta Tempo Min] * [Válidos]
		formatString: 0
		lineageTag: m9

	measure 'Performance %' = DIVIDE([Tempo Necessário Min], [Tempo Disponível Min])
		formatString: 0.0%
		lineageTag: m10

	measure 'Qualidade %' = DIVIDE([Válidos], [Realizados])
		formatString: 0.0%
		lineageTag: m11

	measure 'OPE %' = [Disponibilidade %] * [Performance %] * [Qualidade %]
		formatString: 0.0%
		lineageTag: m12
"""

# Append just before the 'partition F_atendimentos = m' line
import re
match = re.search(r'\s*partition F_atendimentos = m', tmdl)
if match:
    updated = tmdl[:match.start()] + "\n" + new_measures + "\n" + tmdl[match.start():]
    with open("powerbi/Workshop BI.SemanticModel/definition/tables/F_atendimentos.tmdl", "w", encoding="utf-8") as f:
        f.write(updated)
    print("Patched F_atendimentos DAX Measures successfully.")
else:
    print("Could not match partition.")
