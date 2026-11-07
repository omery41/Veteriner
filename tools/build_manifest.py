"""audio/manifest.json dosyasını yazar: sahne kimliği -> mp3 adı. Sadece var olan kayıtları ekler."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
items = json.loads((ROOT / "tools" / "narration.json").read_text("utf-8"))
audio = ROOT / "audio"
audio.mkdir(exist_ok=True)
manifest = {x["id"]: x["hash"] for x in items if (audio / f"{x['hash']}.mp3").exists()}
used = set(manifest.values())
for f in audio.glob("*.mp3"):  # artık kullanılmayan eski kayıtları temizle
    if f.stem not in used and f.stem not in {x["hash"] for x in items}:
        f.unlink()
(audio / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=0), "utf-8")
print(f"Manifest: {len(manifest)}/{len(items)} sahne seslendirildi")
