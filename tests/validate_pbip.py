#!/usr/bin/env python3
"""Validador estatico do projeto BI-OPE (PBIP/TMDL).

Uso (da raiz do repositorio):
    python3 tests/validate_pbip.py

Verifica: JSONs do PBIP/relatorio, estrutura e recursos do TMDL,
relacionamentos, referencias de medidas, residuos de auto date/time
e consistencia entre model.tmdl e as tabelas.
"""
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
PBI = ROOT / "powerbi"
SM = PBI / "Workshop BI.SemanticModel"
DEF = SM / "definition"

fails, oks = [], []


def ok(msg):
    oks.append(msg)


def fail(msg):
    fails.append(msg)


def unquote(name):
    name = name.strip()
    if len(name) >= 2 and name[0] == "'" and name[-1] == "'":
        return name[1:-1]
    return name


# 1) JSONs
json_files = [
    PBI / "Workshop BI.pbip",
    PBI / "Workshop BI.Report" / "definition.pbir",
    SM / "definition.pbism",
    SM / "diagramLayout.json",
    PBI / "Workshop BI.Report" / "definition" / "report.json",
    PBI / "Workshop BI.Report" / "definition" / "version.json",
    PBI / "Workshop BI.Report" / "definition" / "pages" / "pages.json",
]
for jf in json_files:
    try:
        json.load(open(jf, encoding="utf-8-sig"))
        ok("JSON ok: " + str(jf.relative_to(ROOT)))
    except Exception as e:
        fail("JSON invalido: %s -> %s" % (jf.relative_to(ROOT), e))

pages_dir = PBI / "Workshop BI.Report" / "definition" / "pages"
for page_dir in sorted(p for p in pages_dir.iterdir() if p.is_dir()):
    pj = page_dir / "page.json"
    try:
        json.load(open(pj, encoding="utf-8-sig"))
        ok("JSON ok: " + str(pj.relative_to(ROOT)))
    except Exception as e:
        fail("JSON invalido: %s -> %s" % (pj.relative_to(ROOT), e))
    for vj in sorted((page_dir / "visuals").glob("*/visual.json")):
        try:
            json.load(open(vj, encoding="utf-8-sig"))
        except Exception as e:
            fail("JSON invalido: %s -> %s" % (vj.relative_to(ROOT), e))
ok("visuals do relatorio: JSON ok")

# 2) TMDL: indentacao — fora de corpos de conteudo, somente abas.
#    Corpos de MEDIDA/COLUNA (DAX): SOMENTE abas (espacos quebram o parse — caso Paradas Min).
#    Corpos de M/JSON (source=, linguisticMetadata=): verbatim, espacos internos permitidos.
tmdl_all = sorted(DEF.rglob("*.tmdl"))
for tf in tmdl_all:
    lines = open(tf, encoding="utf-8").read().split("\n")
    in_fence = False
    content = None  # (decl_tabs, strict)
    for i, ln in enumerate(lines, 1):
        if "```" in ln:
            in_fence = not in_fence
            continue
        if in_fence or not ln.strip():
            continue
        tabs = len(ln) - len(ln.lstrip("\t"))
        ws = ln[: len(ln) - len(ln.lstrip(" \t"))]
        if content is not None:
            decl_tabs, strict = content
            if tabs > decl_tabs:
                if strict and not re.fullmatch(r"\t+", ws):
                    fail("%s:%d indentacao invalida no corpo DAX (use apenas abas)" % (tf.name, i))
                continue
            content = None  # saiu do corpo; segue para checagem normal
        if ws and not re.fullmatch(r"\t+", ws):
            fail("%s:%d indentacao invalida fora de bloco M (use apenas abas)" % (tf.name, i))
        if ln.rstrip().endswith("="):
            content = (tabs, bool(re.match(r"^\t+(measure|column)\b", ln)))
ok("indentacao dos TMDL por abas (corpos DAX estritos; M/JSON verbatim)")

# 2b) annotations em arquivos de tabela devem estar indentadas (filhas da tabela)
for tf in sorted((DEF / "tables").glob("*.tmdl")):
    for i, ln in enumerate(open(tf, encoding="utf-8").read().split("\n"), 1):
        if re.match(r"^annotation\b", ln):
            fail("%s:%d annotation em coluna 0 (deve ser filha da tabela)" % (tf.name, i))
ok("annotations de tabela indentadas")

# 2c) corpos multi-linha (measure/column com '=' no fim): >= 2 niveis (abas) mais fundo que a declaracao
for tf in tmdl_all:
    lines = open(tf, encoding="utf-8").read().split("\n")
    in_code = False
    for i, ln in enumerate(lines):
        if "```" in ln:
            in_code = not in_code
            continue
        if in_code:
            continue
        if re.match(r"^\t+(measure|column)\b", ln) and ln.rstrip().endswith("="):
            tabs = len(ln) - len(ln.lstrip("\t"))
            j = i + 1
            while j < len(lines) and not lines[j].strip():
                j += 1
            if j < len(lines):
                nxt = lines[j]
                nt = len(nxt) - len(nxt.lstrip("\t"))
                if nxt.strip() and nt < tabs + 2:
                    fail("%s:%d corpo de expressao raso (esperado >= %d abas, tem %d)" % (tf.name, j + 1, tabs + 2, nt))
ok("corpos multi-linha com indentacao profunda (>=2 niveis)")

# 3) tabelas/colunas/medidas
tables, measures = {}, {}
for tf in sorted((DEF / "tables").glob("*.tmdl")):
    text = open(tf, encoding="utf-8").read()
    tname, cols = None, set()
    for ln in text.split("\n"):
        m = re.match(r"^table\s+(.+)$", ln)
        if m:
            tname = unquote(m.group(1))
            continue
        m = re.match(r"^\tcolumn\s+(.+)$", ln)
        if m and tname:
            cols.add(unquote(m.group(1)))
        m = re.match(r"^\tmeasure\s+('([^']+)'|[^=]+?)\s*=", ln)
        if m:
            measures[unquote(m.group(2) or m.group(1))] = ln
    if tname:
        tables[tname] = cols
    else:
        fail(tf.name + ": sem declaracao 'table'")
ok("tabelas TMDL: " + ", ".join(sorted(tables)))

# 4) model.tmdl refs
model = open(DEF / "model.tmdl", encoding="utf-8").read()
refs = set(unquote(x) for x in re.findall(r"^ref table (.+)$", model, re.M))
missing = refs - set(tables)
if missing:
    fail("model.tmdl referencia tabelas inexistentes: %s" % missing)
else:
    ok("model.tmdl: %d refs de tabela ok" % len(refs))
if "ref cultureInfo pt-BR" in model and not (DEF / "cultures" / "pt-BR.tmdl").exists():
    fail("ref cultureInfo pt-BR sem cultures/pt-BR.tmdl")
else:
    ok("cultureInfo pt-BR consistente")

# 5) relacionamentos
rels = open(DEF / "relationships.tmdl", encoding="utf-8").read()
n_rels = 0
for frm, to in re.findall(
    r"fromColumn:\s*(.+?)\s*\n\s*toColumn:\s*(.+?)\s*$", rels, re.M
):
    def split_col(s):
        s = s.strip()
        if "." not in s:
            return None, None
        t, c = s.split(".", 1)
        return unquote(t), unquote(c)

    ft, fc = split_col(frm)
    tt, tc = split_col(to)
    for t_, c_ in ((ft, fc), (tt, tc)):
        if t_ not in tables:
            fail("relacionamento: tabela '%s' inexistente" % t_)
        elif c_ not in tables[t_]:
            fail("relacionamento: coluna '%s.%s' inexistente" % (t_, c_))
    n_rels += 1
ok("%d relacionamentos verificados" % n_rels)

# 6) referencias de medidas a colunas (Table[Col])
for mname, expr in measures.items():
    for t, c in re.findall(
        r"([A-Za-z_][A-Za-z0-9_]*(?:\s+[A-Za-z0-9_]+)*)\[([^\[\]]+)\]", expr
    ):
        t = t.strip()
        if t in tables and c not in tables[t]:
            fail("medida '%s': referencia %s[%s] sem coluna" % (mname, t, c))
ok("%d medidas verificadas" % len(measures))

# 6c) medidas DAX: nao usar apostrofo em volta do nome da tabela (COUNT('T'[Col]))
for mname, expr in measures.items():
    if re.search(r"'F_atendimentos'\[", expr):
        fail("medida '%s': usa 'F_atendimentos'[...] com apostrofo desnecessario" % mname)

# 6d) medidas obsoletas/limitadas nao devem permanecer no modelo
for bad in ["Disponibilidade (Limitada) %", "Performance (Limitada) %", "Qualidade (Limitada) %", "OPE (Limitado) %"]:
    if bad in measures:
        fail("medida obsoleta '%s' ainda presente no modelo" % bad)

# 6b) medidas DAX: refs de medida sem apostrofos e resolviveis
allcols = set()
for tcols in tables.values():
    allcols |= tcols
for mname, expr in measures.items():
    if "['" in expr:
        fail("medida '%s': referencia com apostrofo ['...'] (nao resolve no DAX)" % mname)
    e = re.sub(r'"[^"]*"', '""', expr)
    for ref in sorted(set(re.findall(r"(?<![A-Za-z0-9_\]\)'])\[([^\[\]]+)\]", e))):
        if ref not in measures and ref not in allcols:
            fail("medida '%s': referencia [%s] nao resolve (nem medida nem coluna)" % (mname, ref))
ok("medidas DAX: refs entre colchetes resolviveis")

# 7) residuos proibidos
for tf in tmdl_all:
    txt = open(tf, encoding="utf-8", errors="replace").read()
    for bad in ("VariationSource", "VariationSet", "variation ", "columnID"):
        if bad in txt:
            fail("%s: residuo proibido '%s'" % (tf.relative_to(ROOT), bad))
ok("sem residuos de auto date/time (Variation)")

# 7b) cultures: linguisticMetadata com blob JSON exige contentType: json
cf = DEF / "cultures" / "pt-BR.tmdl"
if cf.exists():
    c = open(cf, encoding="utf-8").read()
    if "linguisticMetadata" in c and "{" in c and "contentType: json" not in c:
        fail("cultures/pt-BR.tmdl: linguisticMetadata sem 'contentType: json' (valida como Xml)")
    else:
        ok("cultures: contentType json ok")

# 8) colunas derivadas: declaradas e produzidas no M
need = [
    "DataOperacional",
    "EquipeNormalizada",
    "EhEquipeCampo",
    "EhEquipeManutencao",
    "EhOperacional",
    "EhImpossibilidade",
    "DuracaoExecucaoMin",
    "Turno",
    "ChaveEquipeDiaTurno",
]

# 8b) colunas derivadas de F_paradas
need_paradas = ["EquipeNormalizada", "EhNaoProgramada", "DataOperacional", "Turno", "ChaveEquipeDiaTurno"]
fpar = tables.get("F_paradas", set())
fpar_text = open(DEF / "tables" / "F_paradas.tmdl", encoding="utf-8").read()
for n in need_paradas:
    if n not in fpar:
        fail("F_paradas sem coluna '%s' declarada" % n)
    if ('"%s"' % n) not in fpar_text:
        fail("M de F_paradas nao produz '%s'" % n)
ok("colunas derivadas de F_paradas declaradas e produzidas (%d/%d)" % (len(need_paradas), len(need_paradas)))

fcol = tables.get("F_atendimentos", set())
fat = open(DEF / "tables" / "F_atendimentos.tmdl", encoding="utf-8").read()
for n in need:
    if n not in fcol:
        fail("F_atendimentos sem coluna '%s' declarada" % n)
    if ('"%s"' % n) not in fat:
        fail("M de F_atendimentos nao produz '%s'" % n)
ok("colunas derivadas declaradas e produzidas (8/8)")

# 9) paginas e pbir
pages = json.load(open(pages_dir / "pages.json", encoding="utf-8-sig"))
for p in pages["pageOrder"]:
    if not (pages_dir / p).exists():
        fail("pages.json referencia pagina inexistente: " + p)
ok("paginas do relatorio consistentes")
pbir = json.load(open(PBI / "Workshop BI.Report" / "definition.pbir", encoding="utf-8-sig"))
target = (PBI / "Workshop BI.Report" / pbir["datasetReference"]["byPath"]["path"]).resolve()
if not target.exists():
    fail("definition.pbir aponta para modelo inexistente")
else:
    ok("definition.pbir -> semantic model ok")

# 9b) visuais: referencias de campo (entidade/coluna/medida) de todos os visual.json
all_measures = set(measures)


def scan_fields(node, out):
    if isinstance(node, dict):
        for k, v in node.items():
            if k in ("Column", "Measure") and isinstance(v, dict):
                prop = v.get("Property") or node.get("Property")
                ent = (v.get("Expression") or {}).get("SourceRef", {}).get("Entity")
                if ent and prop:
                    out.add((k, ent, prop))
            elif k == "Aggregation" and isinstance(v, dict):
                col = (v.get("Expression") or {}).get("Column") or v.get("Column") or {}
                prop = col.get("Property")
                ent = (col.get("Expression") or {}).get("SourceRef", {}).get("Entity")
                if ent and prop:
                    out.add(("Aggregation", ent, prop))
            scan_fields(v, out)
    elif isinstance(node, list):
        for it in node:
            scan_fields(it, out)


nvis, nrefs = 0, 0
for page_dir2 in sorted(p for p in pages_dir.iterdir() if p.is_dir()):
    for vj in sorted((page_dir2 / "visuals").glob("*/visual.json")):
        nvis += 1
        vdata = json.load(open(vj, encoding="utf-8-sig"))
        refs2 = set()
        scan_fields(vdata, refs2)
        for kind, ent, prop in sorted(refs2):
            nrefs += 1
            if ent not in tables:
                fail("%s: entidade '%s' inexistente" % (vj.relative_to(ROOT), ent))
            elif kind == "Measure":
                if prop not in all_measures:
                    fail("%s: medida '%s' inexistente" % (vj.relative_to(ROOT), prop))
            else:
                if prop not in tables[ent]:
                    fail("%s: coluna '%s[%s]' inexistente" % (vj.relative_to(ROOT), ent, prop))
ok("visuais: %d arquivos, %d referencias de campo verificadas" % (nvis, nrefs))

# 9c) tema registrado
rp = json.load(open(PBI / "Workshop BI.Report" / "definition" / "report.json", encoding="utf-8-sig"))
ct = (rp.get("themeCollection") or {}).get("customTheme")
if ct:
    tpath = PBI / "Workshop BI.Report" / "StaticResources" / "RegisteredResources" / (ct.get("name", "") + ".json")
    if ct.get("type") != "RegisteredResources":
        fail("report.json: customTheme.type != RegisteredResources")
    elif not tpath.exists():
        fail("report.json: tema registrado sem arquivo em StaticResources/RegisteredResources")
    else:
        ok("tema '%s' registrado e presente" % ct.get("name"))
if rp.get("filterConfig", {}).get("filters"):
    fail("report.json: filtro global residual (deve estar vazio)")

# 9d) M: Text.Contains/Text.StartsWith devem usar Comparer, nunca Combiner
m_misuse = []
for tmdl_path in sorted((DEF / "tables").glob("*.tmdl")):
    txt = tmdl_path.read_text(encoding="utf-8-sig")
    for m in re.finditer(r'Text\.(Contains|StartsWith)\s*\([^)]*?Combiner\.\w+', txt, re.S):
        m_misuse.append(tmdl_path.name)
if m_misuse:
    fail("M: Text.Contains/Text.StartsWith usando Combiner em vez de Comparer em: " + ", ".join(sorted(set(m_misuse))))
else:
    ok("M: Text.Contains/Text.StartsWith usam Comparer corretamente")

# sumario
for s in oks:
    print("  [ok] " + s)
if fails:
    for s in fails:
        print("  [XX] " + s)
    print("\nRESULTADO: %d FALHA(S), %d OK" % (len(fails), len(oks)))
    sys.exit(1)
print("\nRESULTADO: TUDO OK (%d verificacoes)" % len(oks))
