# PersonaShift: Gerçek Zamanlı Yapay Zeka Tabanlı Yüz Değiştirme ve Görüntü Sentezleme Platformu

## Proje Hakkında
PersonaShift, derin öğrenme ve bilgisayarlı görü (computer vision) teknolojilerini bir araya getirerek canlı kamera akışları üzerinde anlık yüz değiştirme (Face Swap) ve yüksek çözünürlüklü görüntü onarımı (Face Restoration) gerçekleştiren gelişmiş bir masaüstü yazılımıdır. 

Akademik düzeydeki hantal yapay zeka modellerini uçtan uca optimize edilmiş bir işlem hattı (pipeline) mimarisiyle sunan yazılım, standart donanımlara sahip bilgisayarlarda bile son derece düşük gecikme (low latency) ve yüksek kararlılıkla çalışmayı hedefler. 

### Temel Misyon ve Çözülen Problemler
Geleneksel derin sahte (deepfake) ve yüz değiştirme uygulamaları, genellikle hedef kişi özelinde saatler süren model eğitimleri (training), yüksek hesaplama maliyetleri ve teknik bilgi gerektiren karmaşık terminal arayüzleri barındırmaktadır. Ayrıca gerçek zamanlı video akışlarında maske kaymaları, bulanıklık, titreme (flicker) ve ışık uyumsuzlukları gibi görsel bozulmalar (artefaktlar) sıkça yaşanmaktadır.

PersonaShift bu problemleri şu mühendislik çözümleriyle ortadan kaldırır:

* **Çıkarım Odaklı Mimari (Inference-Only):** Yeniden eğitim sürecini tamamen ortadan kaldıran tek atımlık (one-shot) öğrenme yaklaşımı sayesinde, sistem tek bir referans fotoğraf kullanarak saniyeler içinde kimlik aktarımını başlatır.
* **Görsel Gerçekçilik ve Doğal Harmanlama:** Yüz değiştirme işlemi sonrasında oluşan çözünürlük kayıplarını ve pikselleşmeleri üretken onarım katmanlarıyla giderir. Sentetik yüzün renk paletini ve ışık tonlarını kaynak video akışıyla matematiksel olarak harmanlayarak yama görüntüsünü engeller.
* **Evrensel Sanal Kamera Entegrasyonu:** Sistem düzeyinde çalışan sanal kamera sürücüleri sayesinde; Zoom, Microsoft Teams, Discord ve OBS Studio gibi popüler video konferans ve yayın yazılımları tarafından doğrudan fiziksel bir donanım (webcam) gibi algılanır.

### Çekirdek Performans Altyapısı
Uygulamanın motoru, yüz topolojisini milimetrik olarak çıkaran 106 noktalı hassas landmark regresyonu, ONNX Runtime ve NVIDIA CUDA çekirdekleri üzerinde koşan paralel hesaplamalar ile asenkron çoklu iş parçacığı (multi-threading) mimarisine dayanmaktadır. Kullanıcı arayüzü ile yapay zeka işlem hattının tamamen izole edildiği bu kararlı yapı, en ağır grafik yükleri altında bile arayüz donmalarını engeller ve kesintisiz bir kullanıcı deneyimi sunar.


## Kurulum

Proje, standart GitHub dosya boyutu sınırlarını (100 MB) aşan derin öğrenme modelleri barındırdığı için, bu ağır dosyalar depoya (repository) dahil edilmemiştir. Sistemi ayağa kaldırmadan önce modellerin manuel olarak indirilip doğru dizinlere yerleştirilmesi gerekmektedir.

### 1. Yapay Zeka Modellerinin İndirilmesi ve Konumlandırılması

Proje dizininde yer alan `models` klasörü, uygulamanın çekirdek yapay zeka ağırlıklarını barındırır. Aşağıdaki modelleri indirerek belirtilen klasör hiyerarşisine uygun şekilde yerleştirin:

* **InSwapper Modeli (Kimlik Aktarımı):**
    * Yüz değiştirme işlemini yapan ana modeldir.
    * `inswapper_128.onnx` dosyasını indirin ve doğrudan `models/` dizininin köküne yerleştirin.
* **GFPGAN Modeli (HD Restorasyon):**
    * Görüntüdeki bulanıklıkları onaran netleştirme modelidir.
    * `GFPGANv1.4.pth` dosyasını indirin ve doğrudan `models/` dizininin köküne yerleştirin.
* **InsightFace Modelleri (Yüz Tespiti ve Landmark):**
    * Yüz analizi ve koordinat tespiti için gerekli model paketidir.
    * `buffalo_l` paketini (genellikle `.zip` formatında bulunur) indirin.
    * `models/` klasörünün içinde `buffalo_l` adında yeni bir klasör oluşturun.
    * Zip dosyasının içindeki `.onnx` uzantılı 5 adet dosyayı bu klasöre çıkartın.

**Örnek Dosya Hiyerarşisi:**
İndirme ve yerleştirme işlemleri tamamlandığında, uygulamanın çökmeden çalışabilmesi için dosya ağacınız tam olarak aşağıdaki gibi görünmelidir:

```text
PersonaShift/
├── models/
│   ├── buffalo_l/
│   │   ├── 1k3d68.onnx
│   │   ├── 2d106det.onnx
│   │   ├── det_10g.onnx
│   │   ├── genderage.onnx
│   │   └── w600k_r50.onnx
│   ├── GFPGANv1.4.pth
│   └── inswapper_128.onnx
├── src/
├── main.py
└── ...
```


### 2. Kütüphane Kurulumları ve Ortam Hazırlığı

Sistem bağımlılıklarının bilgisayarınızdaki diğer projelerle çakışmaması ve temiz bir kurulum yapılması için Python sanal ortamı (virtual environment) kullanmanız şiddetle tavsiye edilir.

**Adım 1: Sanal Ortam Oluşturma (Önerilen)**
Proje ana dizininde terminalinizi açın ve sanal ortamı oluşturmak için aşağıdaki komutu çalıştırın:
```bash
python -m venv venv
```
Sanal ortamı aktifleştirmek için:
* **Windows Command Prompt:** `venv\Scripts\activate.bat`
* **Windows PowerShell:** `.\venv\Scripts\Activate.ps1`
* **Linux/Mac:** `source venv/bin/activate`

**Adım 2: Temel Bağımlılıkların Yüklenmesi**
Sistemin arayüz (PyQt6), veritabanı bağlantısı ve temel görüntü işleme işlemleri için gereken standart kütüphaneler `requirements.txt` dosyasında listelenmiştir. Yüklemek için komutu çalıştırın:
```bash
pip install -r requirements.txt
```

**Adım 3: GPU Hızlandırma Kütüphaneleri (Kritik Adım)**
PersonaShift'in gerçek zamanlı performansta ve donma olmadan çalışabilmesi için yapay zeka işlemlerinin NVIDIA GPU (CUDA) üzerinde yapılması gerekmektedir. Standart CPU kurulumları 3-4 FPS gibi düşük değerler verecektir.

Aşağıdaki komutlarla CUDA destekli ONNX Runtime'ı kurun:
```bash
pip uninstall onnxruntime onnxruntime-gpu
pip install onnxruntime-gpu
```

Ardından, sisteminizdeki CUDA sürümüne (Örn: CUDA 11.8) uygun PyTorch paketlerini yükleyin. (Aşağıdaki komut CUDA 11.8 içindir, farklı bir sürüm kullanıyorsanız PyTorch'un resmi web sitesinden doğru komutu alabilirsiniz):
```bash
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118
```


### 3. Sanal Kamera (Unity Capture) Sürücü Kurulumu

PersonaShift uygulamasının ürettiği anlık yapay zeka video çıktısını Zoom, Microsoft Teams, Discord veya OBS Studio gibi üçüncü parti platformlara aktarabilmek için işletim sistemine bir sanal kamera DirectShow filtresi kurulması gerekmektedir. Projede bu işlem için yüksek performansı ve sıfıra yakın gecikmesi nedeniyle **Unity Capture** altyapısı tercih edilmiştir.

Sanal kamera sürücüsünü sisteminize tanımlamak için aşağıdaki adımları sırasıyla uygulayın:

**Adım 1: Sürücü Dosyalarını Hazırlayın**
* Sürücü kurulum dosyalarının ve DirectShow filtre kütüphanesinin (`UnityCaptureFilter.dll`) proje dizininde veya ilgili bağımlılık klasöründe hazır bulunduğundan emin olun.

**Adım 2: Filtreyi Sisteme Kaydedin (Yönetici Yetkisi)**
* Sürücü klasörü içerisinde yer alan `Install.bat` (veya kayıt betiği) dosyasına sağ tıklayın.
* **Yönetici Olarak Çalıştır (Run as Administrator)** seçeneğini seçerek betiği tetikleyin.
* Komut satırı penceresinde DirectShow filtresinin işletim sistemine başarıyla kaydedildiğini bildiren onay mesajını (`DllRegisterServer in UnityCaptureFilter.dll succeeded`) kontrol edin.

**Adım 3: Platform Uyumluluk Kontrolü**
* Kayıt işlemi tamamlandıktan sonra bilgisayarınızda bulunan herhangi bir video konferans uygulamasını (örneğin Zoom veya OBS Studio) başlatın.
* Uygulamanın kamera ayarları (Video Input) listesinde **"Unity Video Capture"** adında yeni bir donanım kaynağının listelendiğini doğrulayın.

**Adım 4: pyvirtualcam Bağlantısı**
* PersonaShift çekirdek motoru, `pyvirtualcam` kütüphanesi üzerinden bu DirectShow filtresine asenkron olarak bağlanacak şekilde kurgulanmıştır. Sürücü kurulumu tamamlandıktan sonra `main.py` başlatıldığında, yapay zeka işlem hattından çıkan nihai kareler otomatik olarak bu sanal aygıta yönlendirilir.


### 4. Veritabanı Kurulumu ve Ortam Değişkenleri (.env)

Uygulamanın kullanıcı giriş sistemi, rol yetkilendirmesi (Premium/Standart) ve sistem ayarları PostgreSQL veritabanı üzerinden asenkron olarak yönetilmektedir. Veritabanı altyapısını kurmak için Docker kullanılmaktadır.

**Adım 1: .env Dosyasının Oluşturulması**
Projenin kök dizininde (`main.py` ile aynı yerde) `.env` adında gizli bir dosya oluşturun ve içerisine aşağıdaki veritabanı bağlantı bilgilerini kendi şifrenizle tanımlayın:
```env
DB_USER=postgres
DB_PASSWORD=kendi_sifreniz
DB_HOST=localhost
DB_PORT=5432
DB_NAME=personashift_db
```