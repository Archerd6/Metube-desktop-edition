#!/usr/bin/env python3
import os
import sys
import zipfile
import base64
import textwrap

def get_ui_source():
    base = os.path.dirname(os.path.abspath(__file__))
    candidates = [
        os.path.join(base, 'ui', 'dist', 'metube'),
        os.path.join(base, 'ui', 'dist'),
    ]
    for cand in candidates:
        if os.path.exists(cand):
            return cand
    return None

def create_ui_b64():
    source = get_ui_source()
    if not source:
        print("[ERROR] No se encontró ui/dist/metube")
        print("Ejecuta 'cd ui && npm install && node_modules/.bin/ng build' primero")
        sys.exit(1)

    print(f"[INFO] Creando ui.b64 desde {source}...")

    with zipfile.ZipFile('ui.zip', 'w', zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(source):
            for f in files:
                full = os.path.join(root, f)
                rel = os.path.join('dist', 'metube', os.path.relpath(full, source))
                zf.write(full, rel)

    with open('ui.zip', 'rb') as f:
        data = base64.b64encode(f.read()).decode()

    with open('ui.b64', 'w') as f:
        f.write('\n'.join(textwrap.wrap(data, 76)))

    os.remove('ui.zip')
    print(f"[OK] ui.b64 creado")

def generate_zip_intefaz_web():
    if not os.path.exists('ui.b64'):
        print("[ERROR] No existe ui.b64. Ejecuta primero python build_ui.py")
        sys.exit(1)

    print("[INFO] Generando app/zip_intefaz_web.py...")

    with open('ui.b64', 'r') as f:
        b64_content = f.read()

    template = '''import base64
import zipfile
import io
import os
import sys

# El archivo .b64 se genera:

# Haciendo un zip de la carpeta 'ui' (que contiene la interfaz web)
# y luego convirtieron ese zip a base64 con el siguiente comando:
# python -c "import zipfile,base64,io,textwrap; b=io.BytesIO(); zipfile.ZipFile(fileobj=b,mode='w').write('ui.zip'); s=base64.b64encode(b.getvalue()).decode(); open('ui.b64','w').write('\\\\n'.join(textwrap.wrap(s,76)))"

# --- Contenido ZIP embebido (copiado desde ui.b64) ---
UI_ZIP_BASE64 = b"""
'''

    footer = '''"""

# Carpeta objetivo
if getattr(sys, 'frozen', False):
    # PyInstaller modo exe
    BASE_DIR = os.path.dirname(sys.executable)
else:
    # Modo script
    BASE_DIR = os.path.dirname(__file__)

TARGET_DIR = os.path.join(BASE_DIR, "ui")


def ensure_ui_folder():
    """Comprueba si la carpeta 'ui' existe; si no, la crea desde el ZIP embebido."""
    if not os.path.exists(TARGET_DIR):
        print("[INFO] Carpeta 'ui' no encontrada. Creando desde datos embebidos...")
        data = base64.b64decode(UI_ZIP_BASE64)
        with zipfile.ZipFile(io.BytesIO(data), "r") as zip_ref:
            members = zip_ref.namelist()
            # Detecta si todo empieza con 'ui/'
            prefix = "ui/"
            if all(m.startswith(prefix) for m in members):
                for member in members:
                    # Quita el prefijo 'ui/' si existe
                    new_name = member[len(prefix):] if member.startswith(prefix) else member
                    if not new_name:
                        continue  # ignora entradas vacías
                    target_path = os.path.join(TARGET_DIR, new_name)
                    if member.endswith("/"):
                        # Es un directorio
                        os.makedirs(target_path, exist_ok=True)
                    else:
                        # Es un archivo
                        os.makedirs(os.path.dirname(target_path), exist_ok=True)
                        with zip_ref.open(member) as src, open(target_path, "wb") as dst:
                            dst.write(src.read())
            else:
                zip_ref.extractall(TARGET_DIR)
        print("[OK] Carpeta 'ui' creada correctamente.")
    else:
        print("[OK] Carpeta 'ui' ya existe.")



if __name__ == "__main__":
    ensure_ui_folder()
'''

    with open('app/zip_intefaz_web.py', 'w') as f:
        f.write(template)
        f.write(b64_content)
        f.write(footer)

    print("[OK] app/zip_intefaz_web.py creado")

if __name__ == '__main__':
    create_ui_b64()
    generate_zip_intefaz_web()