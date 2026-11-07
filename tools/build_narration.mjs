// index.html içindeki hastalık verisinden her sahnenin okunacak metnini çıkarır.
// Çıktı: tools/narration.json  ->  [{ id, hash, text }]
import { readFileSync, writeFileSync } from "node:fs";
import { createHash } from "node:crypto";

const VOICE_VERSION = "chatterbox-mtl-tr-v1"; // ses ayarı değişirse tüm kayıtlar yeniden üretilir
const html = readFileSync(new URL("../index.html", import.meta.url), "utf8");
const start = html.indexOf("const D = {");
const end = html.indexOf("/* ---------- Görünümler");
if (start < 0 || end < 0) throw new Error("Hastalık verisi bulunamadı");
const D = new Function(html.slice(start, end) + "\nreturn D;")();

// Uygulamadaki forSpeech() ile aynı kurallar
const forSpeech = (t) => t
  .replace(/%\s?(\d+(?:,\d+)?)/g, "yüzde $1")
  .replace(/(\d+)\s?[–-]\s?(\d+)/g, "$1 ile $2")
  .replace(/°C/g, " derece")
  .replace(/\bkg\b/g, "kilogram")
  .replace(/\bcm\b/g, "santimetre")
  .replace(/\(|\)/g, ", ")
  .replace(/\s+/g, " ")
  .replace(/\s+([,.])/g, "$1")
  .replace(/,\s*,/g, ",")
  .replace(/,\s*([.;:!?])/g, "$1")
  .trim();

const out = [];
for (const [animal, list] of Object.entries(D)) {
  list.forEach((d, i) => {
    const says = [
      `${d.n}. ${d.w}`,
      "Belirtiler. " + d.s.join(". "),
      "Klinikte tedavi. " + d.t.join(". "),
      "Günlük hayatta yapılacaklar. " + d.h.join(". "),
      `Acil durum. ${d.a}`,
    ];
    says.forEach((s, k) => {
      const text = forSpeech(s.endsWith(".") ? s : s + ".");
      const hash = createHash("sha1").update(VOICE_VERSION + "|" + text).digest("hex").slice(0, 16);
      out.push({ id: `${animal}-${i}-${k}`, animal, hash, text });
    });
  });
}
writeFileSync(new URL("./narration.json", import.meta.url), JSON.stringify(out, null, 1));
console.log(`${out.length} sahne, ${out.reduce((a, x) => a + x.text.length, 0)} karakter`);
