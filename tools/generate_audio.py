"""Chatterbox Multilingual (MIT lisanslı) ile her sahnenin Türkçe mp3 kaydını üretir.

Kullanım: python tools/generate_audio.py --animal kedi --out audio --budget-min 300
- tools/narration.json içindeki metinleri okur.
- audio/<hash>.mp3 zaten varsa atlar (metin değişmediyse yeniden üretmez).
- Süre bütçesi dolunca durur; kalanlar bir sonraki çalıştırmada üretilir.
- tools/voice/referans.wav varsa o ses tonu kullanılır.
"""
import argparse, json, os, re, subprocess, sys, tempfile, time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REF = ROOT / "tools" / "voice" / "referans.wav"


def sentences(text):
    parts = [p.strip() for p in re.split(r"(?<=[.!?;:])\s+", text) if p.strip()]
    out = []
    for p in parts:  # çok uzun cümleleri virgülden böl
        while len(p) > 220:
            cut = p.rfind(",", 0, 220)
            if cut < 60:
                break
            out.append(p[: cut + 1].strip())
            p = p[cut + 1 :].strip()
        out.append(p)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--animal", default=None)
    ap.add_argument("--out", default=str(ROOT / "audio"))
    ap.add_argument("--budget-min", type=float, default=300)
    ap.add_argument("--limit", type=int, default=0)
    a = ap.parse_args()
    t_start = time.time()

    items = json.loads((ROOT / "tools" / "narration.json").read_text("utf-8"))
    if a.animal:
        items = [x for x in items if x["animal"] == a.animal]
    out_dir = Path(a.out)
    out_dir.mkdir(parents=True, exist_ok=True)
    todo = [x for x in items if not (out_dir / f"{x['hash']}.mp3").exists()]
    if a.limit:
        todo = todo[: a.limit]
    print(f"{len(items)} sahne, üretilecek: {len(todo)}", flush=True)
    if not todo:
        return

    import torch, torchaudio as ta

    _load = torch.load
    torch.load = lambda *x, **k: _load(*x, **{**k, "map_location": torch.device("cpu")})
    torch.set_num_threads(os.cpu_count() or 4)
    from chatterbox.mtl_tts import ChatterboxMultilingualTTS

    model = ChatterboxMultilingualTTS.from_pretrained(device="cpu")
    sr = model.sr
    gen_kw = dict(language_id="tr", exaggeration=0.55, cfg_weight=0.4, temperature=0.75)
    if REF.exists():
        gen_kw["audio_prompt_path"] = str(REF)
        print("Referans ses kullanılıyor", flush=True)

    pause_short = torch.zeros(1, int(sr * 0.28))
    pause_long = torch.zeros(1, int(sr * 0.5))
    done = 0
    for x in todo:
        if (time.time() - t_start) / 60 > a.budget_min:
            print("Süre bütçesi doldu, kalanlar sonraki çalıştırmada", flush=True)
            break
        try:
            chunks = []
            for j, s in enumerate(sentences(x["text"])):
                with torch.inference_mode():
                    w = model.generate(s, **gen_kw)
                w = w.detach().cpu().float()
                if w.dim() == 1:
                    w = w.unsqueeze(0)
                chunks += [w, pause_long if j == 0 else pause_short]
            wav = torch.cat(chunks, dim=1)
            with tempfile.TemporaryDirectory() as td:
                tmp = Path(td) / "a.wav"
                ta.save(str(tmp), wav, sr)
                subprocess.run(
                    ["ffmpeg", "-y", "-loglevel", "error", "-i", str(tmp),
                     "-af", "loudnorm=I=-16:TP=-1.5:LRA=11,highpass=f=70",
                     "-ac", "1", "-ar", "24000", "-codec:a", "libmp3lame", "-b:a", "64k",
                     str(out_dir / f"{x['hash']}.mp3")],
                    check=True)
            done += 1
            print(f"[{done}/{len(todo)}] {x['id']} hazır ({(time.time()-t_start)/60:.1f} dk)", flush=True)
        except Exception as e:  # tek sahne hatası tüm işi durdurmasın
            print(f"HATA {x['id']}: {e}", file=sys.stderr, flush=True)


if __name__ == "__main__":
    main()
