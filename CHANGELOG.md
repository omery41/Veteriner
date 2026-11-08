# Patiderdi · Sürüm Notları

## 1.8.1 · 8 Kasım 2026
- "Hayvanlarım" bölümünün adı "Patilerim" oldu.

## 1.8.0 · 8 Kasım 2026
- Yeni "Patilerim" bölümü: künye, aşılar, parazit ve ilaçlar, hastalık geçmişi, kilo grafiği, veteriner ziyaretleri. Kayıtlar yalnızca cihazda (localStorage) saklanır.
- "Veterinerime gönder": kayıt sıkıştırılıp bağlantının # kısmına konur (sunucuya gitmez); WhatsApp, e-posta, kopyalama, yazdır/PDF. Bağlantıyı açan "Kayıtlarıma ekle" ile kendi cihazına alabilir.
- Yaklaşan/geciken aşı ve parazit uyarıları, .ics takvim hatırlatması, hastalık geçmişinden anlatıma geçiş, JSON yedek indirme/yükleme.

## 1.7.0 · 8 Kasım 2026
- Hastalık açılınca çubuk kendiliğinden ilerlemiyor; anlatım "Sesi oynat" ya da oynat tuşuyla başlıyor.
- İlerleme çubuğu ve süre kaydın gerçek uzunluğunu izliyor; ses bitmeden sonraki bölüme geçilmiyor.
- Seslendirme kalite kontrolü: kısa cümleler birleştirilerek üretiliyor, fazla uzun (uydurma) ya da kelime atlayan kayıtlar otomatik yeniden üretiliyor. Sorunlu 106 kayıt yenileniyor.

## 1.6.1 · 8 Kasım 2026
- "Sesi oynat" butonuna basınca sesin hiç çıkmaması düzeltildi; ses artık dokunuşla aynı anda başlıyor (iPhone bunu şart koşuyor).
- Telefonda 60 MB indiren ara ses kaldırıldı; stüdyo kayıtları hazır olana kadar cihaz sesi çalıyor.
- Ses takılırsa anlatım beklemeden devam ediyor.

## 1.6.0 · 8 Kasım 2026
- 60 hastalığın tüm bölümleri kontrol edildi; klinik tedavisi 2 maddede kalan 5 hastalık tamamlandı.
- Belirti ve öneri maddeleri bölüm açılır açılmaz görünüyor.
- Her anlatım ekranına kaynak numaraları eklendi; dokununca ilgili makale açılıyor.
- Kaynaklara 5 klinik kılavuz eklendi: WSAVA diş, IRIS böbrek, AAFP hipertiroidi, ICADA atopik dermatit, AAHA kilo yönetimi.

## 1.5.0 · 8 Kasım 2026
- Anlatımlar Chatterbox Multilingual (MIT lisanslı) yapay zekâ sesiyle önceden seslendirilip uygulamaya kayıt olarak eklendi.
- Kayıtlar GitHub sunucularında otomatik üretiliyor; metin değişince ilgili kayıt kendiliğinden yenileniyor.
- Telefona model indirilmiyor; kayıt yoksa önceki ses yedek olarak çalışıyor.

## 1.4.0 · 8 Kasım 2026
- Sesli anlatım artık robotik cihaz sesi yerine doğal bir yapay zekâ Türkçe sesiyle (Piper) yapılıyor.
- Doğal ses ilk kullanımda bir kez indiriliyor, sonra telefonda saklanıyor.
- Yüzde, derece ve aralıklar doğal okunuyor ("yüzde 7", "3 ile 6").
- Doğal ses yüklenemezse cihaz sesi devreye giriyor.

## 1.3.0 · 8 Kasım 2026
- Uygulamanın adı Patiderdi oldu.
- Yeni çizim tarzı simge: yara bantlı pati. Tarayıcı sekmesinde ve iPhone ana ekranında görünür.

## 1.2.1 · 8 Kasım 2026
- Hastalık seçilince anlatım sayfanın altında değil, ekranın tamamında açılıyor.

## 1.2.0 · 8 Kasım 2026
- Sürüm bilgisi ve sürüm notları eklendi (sayfanın en altında, kapalı olarak).

## 1.1.0 · 8 Kasım 2026
- Hamster ve kaplumbağa eklendi, her birinde 10 hastalık.
- Ses artık hastalık seçilince kendiliğinden başlamıyor.
- Alttaki ses butonu kaldırıldı; animasyonun üstüne "Sesi oynat" butonu geldi.
- Cihazdaki en doğal Türkçe ses seçiliyor, metin cümle cümle okunuyor.
- Kaynaklara hamster (2022) ve kaplumbağa (2025) VetCompass çalışmaları eklendi.

## 1.0.0 · 7 Kasım 2026
- İlk sürüm: kedi, köpek, kuş ve tavşan için 10'ar hastalık.
- Her hastalık için 5 bölümlü animasyonlu anlatım: tanım, belirtiler, klinik tedavi, evde bakım, acil durum.
- Akademik kaynak listesi.
