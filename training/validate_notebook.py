import json

with open(r'd:\GUI Duren\GUI Duren\training\DurianVision_Training_Colab.ipynb', 'r', encoding='utf-8') as f:
    nb = json.load(f)

cells = nb['cells']
md_cells = [c for c in cells if c['cell_type'] == 'markdown']
code_cells = [c for c in cells if c['cell_type'] == 'code']

print("=== VALIDASI NOTEBOOK ===")
print(f"Format      : nbformat {nb['nbformat']}.{nb['nbformat_minor']}")
print(f"GPU Type    : {nb['metadata']['colab']['gpuType']}")
print(f"Total cells : {len(cells)}")
print(f"  Markdown  : {len(md_cells)}")
print(f"  Code      : {len(code_cells)}")

# Cek setiap code cell
print("\nDaftar Cell:")
for i, cell in enumerate(cells):
    ctype = cell['cell_type']
    src = ''.join(cell['source'])
    first_line = cell['source'][0].strip() if cell['source'] else '(kosong)'
    if len(first_line) > 60:
        first_line = first_line[:60] + '...'
    print(f"  [{i:2d}] {ctype:8s} | {first_line}")

# Validasi syntax setiap code cell
print("\nValidasi syntax:")
errors = 0
for i, cell in enumerate(cells):
    if cell['cell_type'] == 'code':
        src = ''.join(cell['source'])
        # Hapus magic commands (!) untuk validasi python syntax
        lines = []
        for line in src.split('\n'):
            stripped = line.strip()
            if stripped.startswith('!'):
                lines.append('pass  # shell command')
            else:
                lines.append(line)
        clean_src = '\n'.join(lines)
        try:
            compile(clean_src, f'cell_{i}', 'exec')
            print(f"  [OK] Cell {i}")
        except SyntaxError as e:
            errors += 1
            print(f"  [GAGAL] Cell {i}: {e}")

if errors == 0:
    print("\n✅ Semua code cells memiliki syntax yang valid!")
else:
    print(f"\n❌ {errors} cell memiliki syntax error!")
