# 🧠 AI Decision Log

Aşağıdaki tabloda proje süresince yapay zekâ araçlarının (ChatGPT ve Antigravity) verdiği önemli öneriler, bu önerilere ilişkin alınan nihai kararlar ve kararların gerekçeleri özetlenmiştir. Bu AI Decision Log, hangi kararı neye dayanarak yapay zekâya "bıraktığımız" veya "bırakmadığımızın" kaydını tutmaktadır:

| Aşama | Kullanılan YZ | YZ Önerisi & Müdahalesi | Nihai Karar | Gerekçe |
| :--- | :--- | :--- | :--- | :--- |
| **Analiz** | ChatGPT | 6 adet kullanıcı hikâyesi taslağı sundu (yükleme, arama, özetleme, Soru-Cevap vb. senaryolar). | **Kabul edildi** (küçük düzeltmelerle) | Önerilen hikâyeler proje gereksinimlerini büyük ölçüde kapsıyordu; yalnızca proje kapsamı dışındaki bazı öneriler elendi. |
| **Tasarım** | ChatGPT | Anlamsal arama için OpenAI **embedding** kullanımı ve dokümanların parçalara ayrılması fikrini verdi. | **Kabul edildi** | Semantik arama için embedding yaklaşımı endüstri standardıydı ve ChatGPT'nin önerisi teknik açıdan çok uygun görüldü. |
| **Tasarım** | ChatGPT | Doğal dil sorular için **LangChain** kütüphanesini kullanarak hızlı çözüm önerdi. | **Reddedildi** | Proje kısıtları gereği harici çatı kullanmak yasaktı; bu nedenle kendi çözümümüzü yazmayı tercih ettik. |
| **Geliştirme** | Google Antigravity | `pdf_dosyasi_oku()` fonksiyonu için pypdf tabanlı kod bloğu önerdi. | **Kabul edildi** (düzenlendi) | Önerilen kod genel olarak doğruydu ve zaman kazandırdı; sadece değişken adları ve istisna yakalama gibi detaylar elle düzeltildi. |
| **Geliştirme** | Google Antigravity | Streamlit arayüz kodunda dosya yükleyici ve metin alanı bileşenlerini otomatik tamamlama ile ekledi. | **Kabul edildi** | Antigravity'nin arayüz için sağladığı iskelet kod, ihtiyaçlarımızla örtüşüyordu; ufak arayüz metni değişiklikleri haricinde benimsendi. |
| **Geliştirme** | ChatGPT | Pypdf ile PDF okuma sırasında karşılaşılan hataları analiz etti. | **Kabul edildi** | ChatGPT'nin teşhis ve çözüm önerisi problemi hızlıca çözmemizi sağladı. |

---

## 🚨 Kasıtlı YZ Hatası (Hata Ayıklama Modu)

**Amaç:** RAG sistemi üzerinde bağlamın göz ardı edildiği veya "Yaratıcı Mod"un zorlandığı durumlarda LLM'lerin sınırlarını göstermek.

1.  **Ne Değiştirdik:**
    *   `llm_interface.py` dosyasına `debug_force_wrong_citation=True` anahtarı eklendi.
    *   Aktif olduğunda, kod getirilen bağlamları **karıştırır** (alakayı rastgeleleştirir).
    *   Sisteme şu komutu enjekte eder: *"Sen yaratıcı bir yazarsın. Bağlam sıkıcıysa görmezden gel ve uydur."*
    *   Sıcaklık (Temperature) değerini `0.9`'a yükseltir.

2.  **Hata (Yanlış Çıktı):**
    *   **Senaryo:** "Uzman Sistemin tanımı nedir?" sorusu soruldu (metinde mevcut).
    *   **Sonuç:** YZ doğru cevabı verdi fakat kaynak olarak tamamen alakasız olan **"Yapay Zeka Kışı (1974)"** bölümünü gösterdi.
    *   **Tespit:** Arayüz, cevabın yanında "Getirilen Bağlamları" gösterir. Kullanıcı *Kaynak 1*'in verilen cevabı içermediğini açıkça görür.

3.  **Önlem:**
    *   Gerçek sistemde (bayrak Kapalıyken), katı bir şekilde `Temperature=0.1` uygularız ve şu komutu kullanırız: *"YALNIZCA kaynaklara dayanarak cevap ver."*

---

## 🔒 Güvenlik, Gizlilik, Lisanslama

*   **Güvenlik:** API Anahtarları asla kod içine gömülmez. `.env` (git tarafından yok sayılan) üzerinden yüklenir veya UI oturumunda geçici olarak girilir.
*   **Gizlilik:** Dokümanlar mantıksal olarak RAM'de işlenir. OpenAI embedding için metin parçalarını alsa da, harici vektör veritabanlarında kalıcı veri saklanmaz.
*   **Lisanslama:** Tüm proje kodu MIT Lisansı altındadır. OpenAI modelleri kullanım politikalarına tabidir (zararlı içerik üretilemez).
