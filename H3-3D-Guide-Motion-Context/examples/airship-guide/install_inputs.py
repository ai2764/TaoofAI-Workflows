"""Install only this example's input assets; no model downloads or generation."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil

package = Path(__file__).resolve().parent
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--comfy-root", required=True, type=Path,
                    help="The actual ComfyUI server directory (containing input/)")
parser.add_argument("--check-only", action="store_true")
args = parser.parse_args()
comfy = args.comfy_root.resolve()
manifest = json.loads((package / "manifest.json").read_text(encoding="utf-8"))
for entry in manifest["files"]:
    source = (package / entry["path"]).resolve()
    target = (comfy / entry["path"]).resolve()
    if not source.is_relative_to(package) or not target.is_relative_to(comfy / "input"):
        raise SystemExit("Input path leaves the expected input directory")
    digest = hashlib.sha256(source.read_bytes()).hexdigest()
    if digest != entry["sha256"]:
        raise SystemExit(f"Downloaded input checksum differs: {entry['path']}")
    if args.check_only:
        if not target.is_file() or hashlib.sha256(target.read_bytes()).hexdigest() != digest:
            raise SystemExit(f"Missing/different installed input: {target}")
    elif target.exists():
        if hashlib.sha256(target.read_bytes()).hexdigest() != digest:
            raise SystemExit(f"Refusing to replace another file: {target}")
    else:
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
    print(f"OK: {entry['path']}")
print("Input files verified. This does not install models or run generation.")
