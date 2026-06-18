import os
import sys
from PyQt6.QtWidgets import QApplication, QDialog
from ui import LoginDialog, MainWindow

if getattr(sys, 'frozen', False):
    sys.path.append(os.path.join(sys._MEIPASS, 'basicsr'))
    sys.path.append(os.path.join(sys._MEIPASS, 'gfpgan'))

if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    
    # Giriş ekranını oluştur ve göster
    login_screen = LoginDialog()
    
    # Kullanıcı doğru şifre girip "Giriş Yap"a basarsa
    if login_screen.exec() == QDialog.DialogCode.Accepted:
        # Ana pencereyi veritabanından gelen verilerle başlat
        window = MainWindow(login_screen.full_name, login_screen.is_premium)
        window.show()
        sys.exit(app.exec())