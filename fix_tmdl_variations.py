import glob, re

files = glob.glob("powerbi/Workshop BI.SemanticModel/definition/tables/*.tmdl")
for path in files:
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    # The pattern matches \n (two tabs) variation (anything) \n (three tabs) (anything) \n
    # and removes the whole block.
    # We will loop replacing it to handle multiple instances.
    old_content = ""
    while old_content != content:
        old_content = content
        # Matches variation declaration and all subsequent lines starting with 3 tabs
        # or it could be 2 tabs + 1 space... let's just match the specific known properties.
        content = re.sub(r'\n\t\tvariation .*?(?:\n\t\t\t[^\n]+)*', '', content)
        
    if content != old_content:
        pass # just checking

    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Cleaned variations in {path}")
