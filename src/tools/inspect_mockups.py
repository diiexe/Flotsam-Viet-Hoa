import os, re, json

def get_valid_term_name(text, allow_category=False):
    if text is None: return None
    sb = []
    flag = False
    c = '\0'
    flag2 = False
    valid_symbols = ".-_$#@*()[]{}+:?!&',^=<>~`"
    for i, c2 in enumerate(text):
        flag3 = True
        if (c2 in '{[<') and not flag:
            if c2 != '{' or i + 1 >= len(text) or text[i+1] == '[':
                flag = True
                flag3 = False
                c = c2
        elif flag and ((c2 == '}' and c == '{') or (c2 == ']' and c == '[') or (c2 == '>' and c == '<')):
            flag = False
            flag3 = False
        elif flag:
            flag3 = False
        if not flag3:
            continue
        value = ' '
        if (allow_category and c2 in '\\"/') or c2.isalnum() or c2 in valid_symbols:
            value = c2
        if c2.isspace():
            if not flag2:
                if len(sb) > 0:
                    sb.append(' ')
                flag2 = True
        else:
            flag2 = False
            sb.append(value)
    return ''.join(sb)

game_dir = r'C:\Program Files\Epic Games\Flotsam\Flotsam_Data'
targets = ['sharedassets0.assets', 'sharedassets2.assets', 'level1', 'level2']
mockup_pat = re.compile(rb'Well this is a mockup description[^\x00]*')

raw_strings = set()
for t in targets:
    p = os.path.join(game_dir, t)
    data = open(p, 'rb').read()
    for m in mockup_pat.findall(data):
        s = m.decode('utf-8', errors='ignore')
        raw_strings.add(s)

print(f"Found {len(raw_strings)} unique raw strings:")
results = []
for s in sorted(raw_strings):
    norm = get_valid_term_name(s)
    results.append((s, norm))
    print("RAW:", repr(s))
    print("NORMALIZED:", repr(norm))
    print("-" * 50)

with open(r'C:\Users\Diiexe\.gemini\antigravity\brain\e92d823e-d89c-4d0c-be51-b83a428ed0fc\VietHoa_Flotsam_Safe_Storage\mockups_analysis.json', 'w', encoding='utf-8') as f:
    json.dump([{'raw': r, 'norm': n} for r, n in results], f, ensure_ascii=False, indent=2)