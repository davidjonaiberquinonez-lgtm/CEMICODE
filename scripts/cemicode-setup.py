"""CEMICODE Setup — instalador portable a .exe (paso dos).
Busca CEMICODE-Portable.zip junto al Setup, lo extrae a destino,
crea accesos directos y opcionalmente agrega a PATH.
Uso: CEMICODE-Setup.exe [--dir "C:\\CEMICODE"] [--no-shortcuts] [--add-path]
"""
import os, sys, shutil, zipfile, subprocess
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

APP = "CEMICODE"
DEFAULT_DIR = Path(os.environ.get("LOCALAPPDATA", str(Path.home()))) / APP

def find_zip():
    here = Path(sys.executable).parent if getattr(sys, "frozen", False) else Path(__file__).resolve().parents[1] / "dist"
    candidates = [here / "CEMICODE-Portable.zip", Path.cwd() / "CEMICODE-Portable.zip",
                  Path(__file__).resolve().parents[1] / "dist" / "CEMICODE-Portable.zip"]
    for c in candidates:
        if c.exists():
            return c
    return None

def ps(cmd):
    subprocess.run(["powershell", "-NoProfile", "-Command", cmd], check=False)

def make_shortcut(target, lnk, desc, workdir, icon=None):
    icon_part = f"$s.IconLocation = '{icon}'; " if icon else ""
    cmd = (f"$ws = New-Object -ComObject WScript.Shell; "
           f"$s = $ws.CreateShortcut('{lnk}'); $s.TargetPath = '{target}'; "
           f"$s.WorkingDirectory = '{workdir}'; $s.Description = '{desc}'; "
           f"{icon_part}$s.Save()")
    ps(cmd)

def main():
    args = sys.argv[1:]
    dest = Path(args[args.index("--dir") + 1]) if "--dir" in args else DEFAULT_DIR
    no_sc = "--no-shortcuts" in args
    add_path = "--add-path" in args
    print(f"[{APP} Setup] Destino: {dest}")
    z = find_zip()
    if not z:
        print("ERROR: no se encontro CEMICODE-Portable.zip junto al Setup.", file=sys.stderr)
        print("Coloca CEMICODE-Portable.zip en la misma carpeta que CEMICODE-Setup.exe", file=sys.stderr)
        return 1
    print(f"[{APP} Setup] Extrayendo {z.name} ({z.stat().st_size // 1024 // 1024} MB)...")
    dest.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(z) as zh:
        # El zip contiene carpeta raiz dist-portable-cemicode/ -> extraer contenido plano
        for m in zh.namelist():
            parts = m.split("/", 1)
            rel = parts[1] if len(parts) == 2 and parts[0].startswith("dist-portable") else m
            if not rel:
                continue
            out = dest / rel
            if m.endswith("/"):
                out.mkdir(parents=True, exist_ok=True)
            else:
                out.parent.mkdir(parents=True, exist_ok=True)
                with zh.open(m) as src, open(out, "wb") as fh:
                    shutil.copyfileobj(src, fh)
    print(f"[{APP} Setup] Archivos listos en {dest}")
    if not no_sc:
        desktop = Path(os.environ.get("USERPROFILE", str(Path.home()))) / "Desktop"
        start = Path(os.environ.get("APPDATA", "")) / "Microsoft" / "Windows" / "Start Menu" / "Programs" / APP
        start.mkdir(parents=True, exist_ok=True)
        bat = dest / "ejecutar-cemicode.bat"
        web = dest / "ejecutar-cemicode-web.bat"
        ico = dest / "cemicode.ico"
        icon = str(ico) if ico.exists() else None
        if bat.exists():
            make_shortcut(str(bat), str(desktop / f"{APP}.lnk"), f"{APP} Portable", str(dest), icon)
            make_shortcut(str(bat), str(start / f"{APP}.lnk"), f"{APP} Portable", str(dest), icon)
        if web.exists():
            make_shortcut(str(web), str(start / f"{APP} Web.lnk"), f"{APP} Web", str(dest), icon)
        print(f"[{APP} Setup] Accesos directos creados.")
    if add_path:
        ps(f"[Environment]::SetEnvironmentVariable('Path', [Environment]::GetEnvironmentVariable('Path','User') + ';{dest / 'bin'}', 'User')")
        print(f"[{APP} Setup] Agregado a PATH usuario.")
    print(f"[{APP} Setup] OK. Ejecuta {dest / 'ejecutar-cemicode.bat'}")
    print("Si es primera vez: edita .env con tu DGX_CLAVE y corre bin\\cemicode-auth.exe login")
    return 0

if __name__ == "__main__":
    sys.exit(main())
