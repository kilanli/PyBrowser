from PyQt5.QtWidgets import QApplication,QMainWindow,QToolBar,QAction,QLineEdit,QTabWidget,QToolButton,QWidget,QMenu,QFileDialog,QMessageBox,QTabBar,QLabel
from PyQt5.QtWebEngineWidgets import QWebEngineView,QWebEngineDownloadItem
from PyQt5.QtCore import QUrl,QTimer
from PyQt5.QtGui import QIcon,QPixmap
from datetime import datetime
import os,sys


class Tarayici(QMainWindow):
    def __init__(self):
        super().__init__()
        def kaynak_yolu(goreceli_yol):
            if hasattr(sys, '_MEIPASS'):
                return os.path.join(sys. _MEIPASS,goreceli_yol)
            return os.path.join(os.path.abspath("."),goreceli_yol)
        #Tarayıcımızın ismi ve ikonu belirlendi
        self.setWindowTitle("Tarayici")
        self.setWindowIcon(QIcon(kaynak_yolu("browser_icon.ico")))

        #kullanıcı ekran boyutuna göre taryıcı boyutu ayarlandı
        ekran=QApplication.primaryScreen()
        ekran_boyutu=ekran.size()
        self.resize(ekran_boyutu.width()//2,ekran_boyutu.height()//2)
        self.baslangic_resmi=QLabel(self)
        self.baslangic_resmi.setPixmap(QPixmap(kaynak_yolu("acilis.jpeg")))
        self.baslangic_resmi.setScaledContents(True)
        self.baslangic_resmi.setGeometry(self.rect())
        QTimer.singleShot(500,self.resmi_gizle)

    def resmi_gizle(self):
        self.baslangic_resmi.hide()
        # sekme oluşturduğumuz takdirde bu sekmelerin nasıl davranması gerektiği ile alakalı kod yazıldı
        self.sekmeler = QTabWidget()
        self.setCentralWidget(self.sekmeler)
        self.sekmeler.setTabsClosable(True)
        self.sekmeler.tabCloseRequested.connect(self.sekme_kapat)
        # aşağıdaki fonkumuza ilk sekmeyi google olarak açması için param gönderdik ismini Yeni sekme yerine google yaptık
        self.yeni_sekme(QUrl("https://www.google.com"), "Google")
        # Gezinme çubuğu fonk çağrılarak sekmeler arası ileri ve geri gitmemiz sağlandı
        self.gezinme_cubugu_olustur()
        self.yer_imleri = []
        self.gecmis = []
        self.arti_butonu()
    #Yeni sekmeleri boş sekme olarak açmamızı sağlayan fonk
    def yeni_sekme(self,qurl=None,etiket="Yeni sekme"):
        try:
            tarayici=QWebEngineView()

            if qurl:
                tarayici.setUrl(qurl)
            else:
                tarayici.setUrl(QUrl("about:blank"))

            #Verdiğimiz sekmelerin isimleriyle beraber açılmasını ve yeni sekmenin o sekmenin sağında açılması sağlandı
            index=self.sekmeler.count()-1
            self.sekmeler.insertTab(index,tarayici,etiket)
            self.sekmeler.setCurrentIndex(index)
            tarayici.titleChanged.connect(lambda baslik,tarayici = tarayici: self.sekme_basligi_guncelle(baslik,tarayici))
            tarayici.urlChanged.connect(lambda q: self.url_guncelle(q,tarayici))

            tarayici.urlChanged.connect(self.gecmise_ekle)
            tarayici.page().profile().downloadRequested.connect(self.indirme_yonet)


        except Exception as e:
            print(e)

    def gezinme_cubugu_olustur(self):
        #Gezinme Çubuğu
        navbar=QToolBar()
        self.addToolBar(navbar)

        #Geri Butonu
        geri_buton=QAction("Önceki sekme",self)
        geri_buton.triggered.connect(lambda:self.sekmeler.currentWidget().back())
        navbar.addAction(geri_buton)

        # İleri Butonu
        ileri_buton = QAction("Sonraki sekme", self)
        ileri_buton.triggered.connect(lambda: self.sekmeler.currentWidget().forward())
        navbar.addAction(ileri_buton)

        # Yenile Butonu
        yenile_buton = QAction("Yenile", self)
        yenile_buton.triggered.connect(lambda: self.sekmeler.currentWidget().reload())
        navbar.addAction(yenile_buton)

        #Sekme üstünde arama yapma
        self.url_cubugu=QLineEdit()
        self.url_cubugu.setPlaceholderText("URL gir veya arama yap")
        self.url_cubugu.returnPressed.connect(self.url_yukle_ara)
        navbar.addWidget(self.url_cubugu)


        yer_imleri_menu=QMenu("Yer İmleri",self)
        navbar.addAction(yer_imleri_menu.menuAction())
        yer_imi_ekle_button=QAction("Bu sayfayı yer imlerine ekle.",self)
        yer_imi_ekle_button.triggered.connect(self.yer_imleri_ekle)
        navbar.addAction(yer_imi_ekle_button)
        self.yer_imleri_menu=yer_imleri_menu

        gecmis_menu=QMenu("Gecmis",self)
        navbar.addAction(gecmis_menu.menuAction())
        self.gecmis_menu=gecmis_menu
        self.sekmeler.currentChanged.connect(self.url_cubuk_guncelle)




    def url_yukle_ara(self):
        #eğer site url'i girilirse direk siteye bağlanmasını istedik
        try:
            url=self.url_cubugu.text()
            if "." in url:
                if not url.startswith("http") :
                    url="https://"+url
                self.sekmeler.currentWidget().setUrl(QUrl(url))
        #site url'i yerine bir yazı yazılırsa google daki sonuçları kullanıcıya döndürdük
            else:
                arama_url=f"https://www.google.com/search?q={url}"
                self.sekmeler.currentWidget().setUrl(QUrl(arama_url))
        except Exception as e:
            print(e)

    #Yeni sekmede girilen url veya başlığı sekme başlığı yapıyoruz
    def sekme_basligi_guncelle(self,baslik,tarayici):
        try:
            i=self.sekmeler.indexOf(tarayici)
            if i !=-1:
                self.sekmeler.setTabText(i,baslik)
        except Exception as e:
            print(e)

    #url çubuğunda tüm urli yazılması sağlanıyor
    def url_guncelle(self,q,tarayici=None):
        try:
            if tarayici==self.sekmeler.currentWidget():
                self.url_cubugu.setText(q.toString())

        except Exception as e:
            print(e)

    def yer_imi_menu_ekle(self,baslik,url):
        yer_im_aksiyon=QAction(baslik,self)
        yer_im_aksiyon.triggered.connect(lambda: self.yer_imi_yukle(url) )
        self.yer_imleri_menu.addAction(yer_im_aksiyon)

    def yer_imleri_ekle(self):
        mevcut_widget=self.sekmeler.currentWidget()
        if isinstance(mevcut_widget,QWebEngineView):
            url=mevcut_widget.url().toString()
            baslik=mevcut_widget.title()

            #url in mevcut olması halinde ekleme yapmaması sağlanıyor
            if url not in [yer_im["url"] for  yer_im in self.yer_imleri]:
                self.yer_imleri.append({"baslik":baslik,"url":url})
                self.yer_imi_menu_ekle(baslik,url)


    def yer_imleri_yukle(self,url):
        self.sekmeler.currentWidget().setUrl(QUrl(url))


    def gecmise_ekle(self):
        mevcut_widget=self.sekmeler.currentWidget()
        if isinstance(mevcut_widget,QWebEngineView):
            url=mevcut_widget.url().toString()
            baslik=mevcut_widget.title()

            if url not in [entry["url"] for entry in self.gecmis]:
                ziyaret_zamani=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                url_ozeti=self.url_kisalt(url)
                self.gecmis.append({"baslik":baslik,"url":url,"zaman":ziyaret_zamani})
                self.gecmise_menu_ekle(ziyaret_zamani,url_ozeti,url)


    def gecmise_menu_ekle(self,ziyaret_zamani,url_ozeti,url):
        gecmis_aksiyon=QAction(f"{ziyaret_zamani} - {url_ozeti}",self)
        gecmis_aksiyon.triggered.connect(lambda :self.yer_imleri_yukle(url))
        self.gecmis_menu.addAction(gecmis_aksiyon)

    def url_kisalt(self,url,max_uzunluk=50):
        if len(url)>max_uzunluk:
            return url[:max_uzunluk]+"..."
        return url

    def arti_butonu(self):
        arti_butonu=QToolButton()
        arti_butonu.setText("+")
        arti_butonu.clicked.connect(self.yeni_sekme)
        self.sekmeler.addTab(QWidget(),"")
        self.sekmeler.tabBar().setTabButton(self.sekmeler.count()-1,QTabBar.RightSide,arti_butonu  )
        self.sekmeler.tabBar().setTabEnabled(self.sekmeler.count()-1,False)

    def sekme_kapat(self,i):
        try:
            if self.sekmeler.count()>2:
                self.sekmeler.removeTab(i)

                if i >0:
                    self.sekmeler.setCurrentIndex(i-1)
                else:
                    self.sekmeler.setCurrentIndex(0)

        except Exception as e:
            print(e)

    def url_cubuk_guncelle(self,i):
        try:
            mevcut_widget=self.sekmeler.currentWidget()
            if isinstance(mevcut_widget,QWebEngineView):
                qurl=mevcut_widget.url()
                if qurl.toString()=="about:blank":
                    self.url_cubugu.clear()
                else:
                    self.url_cubugu.setText(qurl.toString())
            else:
                self.url_cubugu.setText(qurl.toString())

        except Exception as e:
            print(e)

    def indirme_yonet(self,indirme_item:QWebEngineDownloadItem):
        dosya_yolu,=QFileDialog.getSaveFileName(self,"Dosyayı Kaydet",indirme_item.suggestedFileName())

        if dosya_yolu:
            indirme_item.setPath(dosya_yolu)
            indirme_item.accept()

        indirme_item.finished.connect(lambda : self.indirme_bilgi(indirme_item))
    def indirme_bilgi(self,indirme_item:QWebEngineDownloadItem):
        if indirme_item.state()==QWebEngineDownloadItem.DownloadCompleted:
            QMessageBox.information(self,"İndirme tamamlanmıştır..",f"İndirme başarıyla tamamlanmıştır:{indirme_item.path()}")
        elif indirme_item.state()==QWebEngineDownloadItem.DownloadCancelled:
            QMessageBox.information(self,"İndirme İptal edildi..","Kontrol Edin")
        elif indirme_item.state()==QWebEngineDownloadItem.DownloadInterrupted:
            QMessageBox.critical(self,"İndirme başarısız..","Kontrol Edin")



uygulama=QApplication(sys.argv)
uygulama.setStyleSheet("""
 QWidget {
 font-size:14px;
 }
 QLineEdit {
 font-size:14px;
 }
 QTabBar::tab {
 font-size:14px;
 }
 QToolButton {
 font-size:14px;
 }
"""
)
pencere=Tarayici()
pencere.show()
sys.exit(uygulama.exec_())