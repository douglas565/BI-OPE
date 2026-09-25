with open("powerbi/Workshop BI.SemanticModel/definition/tables/F_atendimentos.tmdl", "r", encoding="utf-8") as f:
    tmdl = f.read()

new_measures = """
	measure 'Disponibilidade (Limitada) %' = IF([Disponibilidade %] > 1, 1, [Disponibilidade %])
		formatString: 0.0%
		lineageTag: m13

	measure 'Performance (Limitada) %' = IF([Performance %] > 1, 1, [Performance %])
		formatString: 0.0%
		lineageTag: m14

	measure 'Qualidade (Limitada) %' = IF([Qualidade %] > 1, 1, [Qualidade %])
		formatString: 0.0%
		lineageTag: m15

	measure 'OPE (Limitado) %' = [Disponibilidade (Limitada) %] * [Performance (Limitada) %] * [Qualidade (Limitada) %]
		formatString: 0.0%
		lineageTag: m16
"""

import re
match = re.search(r'\s*partition F_atendimentos = m', tmdl)
if match:
    updated = tmdl[:match.start()] + "\n" + new_measures + "\n" + tmdl[match.start():]
    with open("powerbi/Workshop BI.SemanticModel/definition/tables/F_atendimentos.tmdl", "w", encoding="utf-8") as f:
        f.write(updated)
    print("Patched F_atendimentos Capped Measures successfully.")
