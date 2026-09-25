import glob

files = glob.glob("powerbi/Workshop BI.SemanticModel/definition/tables/*.tmdl")
for path in files:
    with open(path, "r", encoding="utf-8") as f:
        lines = f.readlines()
        
    out_lines = []
    skip = False
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("variation Variation") or stripped == "Variation":
            skip = True
            continue
        if skip:
            # if we see properties that belong to variation
            if stripped == "isDefault" or stripped.startswith("relationship:") or stripped.startswith("defaultHierarchy:"):
                continue
            else:
                skip = False
                
        if not skip:
            out_lines.append(line)
            
    with open(path, "w", encoding="utf-8") as f:
        f.write("".join(out_lines))
        
print("Fixed lines globally")
