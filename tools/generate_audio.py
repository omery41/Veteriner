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
        while len(p) > 200:
            cut = p.rfind(",", 0, 200)
            if cut < 60:
                break
            out.append(p[: cut + 1].strip())
            p = p[cut + 1 :].strip()
        out.append(p)
    return out


def chunks_of(text, min_len=55, max_len=200):
    """Kısa cümleleri birleştirir. Chatterbox tek kelimelik girdilerde uydurma ses üretebiliyor
    ("Kanama." gibi), bu yüzden her parça en az ~55 karakter olur."""
    out = []
    for s in sentences(text):
        if out and (len(out[-1]) < min_len or len(s) < 25) and len(out[-1]) + len(s) + 1 <= max_len:
            out[-1] += " " + s
        else:
            out.append(s)
    if len(out) > 1 and len(out[-1]) < 25:
        out[-2] += " " + out.pop()
    return out


def trim(w, sr, thr=0.01):
    """Baştaki ve sondaki sessizliği/nefes artığını kırpar."""
    a = w.abs().squeeze(0)
    win = int(sr * 0.02)
    if a.numel() < win * 3:
        return w
    env = a[: a.numel() // win * win].view(-1, win).max(dim=1).values
    idx = (env > thr).nonzero().squeeze(1)
    if idx.numel() == 0:
        return w
    s0 = max(0, int(idx[0]) * win - int(sr * 0.05))
    s1 = min(a.numel(), (int(idx[-1]) + 1) * win + int(sr * 0.12))
    return w[:, s0:s1]


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
    gen_kw = dict(language_id="tr", exaggeration=0.5, cfg_weight=0.4, temperature=0.65)
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
            for j, s in enumerate(chunks_of(x["text"])):
                # Kalite kontrolü: Türkçe konuşma ~11 karakter/sn. Çok uzun çıkan (uydurma/tekrar)
                # ya da çok kısa çıkan (kelime atlayan) denemeleri yeniden üretir, en iyisini seçer.
                target = len(s) / 11.0
                best = None
                for attempt in range(5):
                    torch.manual_seed(int(x["hash"][:8], 16) + j * 101 + attempt * 7919)
                    with torch.inference_mode():
                        w = model.generate(s, **gen_kw)
                    w = w.detach().cpu().float()
                    if w.dim() == 1:
                        w = w.unsqueeze(0)
                    w = trim(w, sr)
                    dur = w.shape[1] / sr
                    err = abs(dur - target) / target
                    if best is None or err < best[0]:
                        best = (err, w)
                    if len(s) / 15.5 <= dur <= len(s) / 8.0 + 0.8:
                        break
                    print(f"  yeniden: {x['id']} parça {j} ({dur:.1f}s, hedef {target:.1f}s)", flush=True)
                chunks += [best[1], pause_long if j == 0 else pause_short]
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
