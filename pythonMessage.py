#install pyrebase
#install pyqt5 pyuic5-tool
#install plugins pyqtintegration

import pyrebase as pyrebase
import hashlib
import time
import threading

config = {
    'apiKey': "AIzaSyConbfP3NLzDGtQzC3tFsPTeGGYer61FIA",
    'authDomain': "latihanpy.firebaseapp.com",
    'projectId': "latihanpy",
    'storageBucket': "latihanpy.appspot.com",
    'messagingSenderId': "208870694505",
    'appId': "1:208870694505:web:7019458e7965972ae04cf8",
    'databaseURL' : 'https://latihanpy-default-rtdb.firebaseio.com/'
}
firebase = pyrebase.initialize_app(config)
storage = firebase.storage()
database = firebase.database()

from PyQt5 import QtCore, QtGui, QtWidgets
from Ui_window import Ui_Dialog
from PyQt5.QtWidgets import QFileDialog
from PyQt5.QtGui import QKeySequence
import sys
i

class globalVar:
    statusAktif = False
    attach = ''
    filename = ''
    hashval = ''

class mainProgram(QtWidgets.QMainWindow, Ui_Dialog):
    def __init__(self, parent=None):
        super(mainProgram, self).__init__(parent)
        self.setupUi(self)
        self.sendButton.clicked.connect(self.send)
        self.attachButton.clicked.connect(self.attach)
        self.loadButton.clicked.connect(self.load)
        self.buatBaru.stateChanged.connect(self.check)
        self.attachState.stateChanged.connect(self.attachCheck)
        globalVar.statusAktif = False
    def closeEvent(self, event):
        globalVar.statusAktif = False
    def check(self):
        if(self.buatBaru.isChecked()):
            self.peringatan_3.setEnabled(False)
            self.friendID.setEnabled(False)
            self.loadButton.setText("Create")
        else:
            self.peringatan_3.setEnabled(True)
            self.friendID.setEnabled(True)
            self.loadButton.setText("Connect")

    def send(self):
        if(globalVar.statusAktif):
            data = self.inputBox.toPlainText()
            if(data == '' and not self.attachState.isChecked()):
                self.peringatan.setText('Tulis pesannya terlebih dahulu')
                return
            val = {
                    'text':data,
                    'active':True,
                    'url':''
                }
            if(self.attachState.isChecked()):
                url = storage.child(globalVar.hashval + '/' + globalVar.filename).put(globalVar.attach)
                val['url'] = storage.child(globalVar.hashval + '/' + globalVar.filename).get_url(None)
                val['name'] = globalVar.filename
                print(val['url'])
            
            val = database.child('chats').child(globalVar.hashval).child(self.myID.text() + self.friendID.text()).child(int(time.time())).set(val)
            if(val['active'] == True):
                self.inputBox.setPlainText('')
                self.chatRoom.insertHtml('<p><span style="color: black;">{}>> </span>'.format(self.myID.text()))
                if(self.attachState.isChecked()):
                    self.chatRoom.insertHtml('[<a href="{}">{}</a>] '.format(val['url'], globalVar.filename))
                    self.attachState.setEnabled(False)
                    self.attachButton.setEnabled(True)
                    self.attachState.setChecked(False)
                self.chatRoom.insertHtml('<span style="color: black;">{}<br><br></span></p>'.format(data))
                self.peringatan.setText('Pesan Terkirim')
                self.chatRoom.verticalScrollBar().setValue(self.chatRoom.verticalScrollBar().maximum())
            else:
                self.peringatan.setText('Pesan tidak dapat terkirim')
                return
    def listening(self):
        print('Listening Start')
        while globalVar.statusAktif:
            time.sleep(0.5)
            print('listening on : ' + globalVar.hashval)
            onID = self.friendID.text() + self.myID.text()
            val = database.child('chats').child(globalVar.hashval).child(onID).get().val()
            if(str(val) != 'None'):
                print('Has Value\n' + str(val))
                database.child('chats').child(globalVar.hashval).child(onID).set(None)
                outVal = '<p>'
                for data in val.items():
                    print(data)
                    outVal += ('<span style="color: red;">{}>> </span>'.format(self.friendID.text()))
                    if(not data[1]['url'] == ''): outVal += ('[<a href="{}">{}</a>] '.format(data[1]['url'], data[1]['name']))
                    outVal += ('<span style="color: red;">{}<br><br></span>'.format(data[1]['text']))
                self.chatRoom.insertHtml(outVal + '</p>')
                self.chatRoom.verticalScrollBar().setValue(self.chatRoom.verticalScrollBar().maximum())
        print('Listening Stop')
    def load(self):
        if(not globalVar.statusAktif):
            if(self.myID.text() == ''):
                self.peringatan.setText('Masukkan ID anda')
                return
            if(self.myID.text().find('@') == -1 or len(self.myID.text()) < 4) or not self.myID.text().find(' ') == -1:
                self.peringatan.setText('ID anda salah')
                return
            if(self.myPass.text() == ''):
                self.peringatan.setText('Masukkan password anda')
                return
            if(self.buatBaru.isChecked()):
                val = database.child('users').child(self.myID.text()).child('active').get().val()
                print('Out : ' + str(val))
                if(str(val) == 'True'):
                    self.peringatan.setText('ID Sudah digunakan')
                    return
                elif(str(val) == 'None' or str(val) == 'False'):
                    passHash = hashlib.md5(self.myPass.text().encode()).hexdigest()
                    dataOut = {
                        'hash':passHash,
                        'active':True
                    }
                    val = database.child('users').child(self.myID.text()).set(dataOut)
                    print('In : ' + str(val))
                    if(str(val['active']) == 'True'):
                        self.buatBaru.setChecked(False)
                        self.peringatan_3.setEnabled(True)
                        self.friendID.setEnabled(True)
                        self.loadButton.setText("Connect")
                        self.peringatan.setText('ID Berhasil Dibuat')
                        return
                    else:
                        self.peringatan.setText('Error : ' + str(val))
                        return
                else:
                    self.peringatan.setText('Error : ' + str(val))
                    return
            else:
                if(self.friendID.text() == ''):
                    self.peringatan.setText('Masukkan ID teman anda')
                    return
                if(self.friendID.text().find('@') == -1 or len(self.friendID.text()) < 4 or not self.friendID.text().find(' ') == -1):
                    self.peringatan.setText('ID teman anda salah')
                    return
                if(self.friendID.text() == self.myID.text()):
                    self.peringatan.setText('ID teman anda dan anda tidak mungkin sama')
                    return
                val = database.child('users').child(self.myID.text()).get().val()
                print('Out Me : ' + str(val))
                if(str(val) == 'None' or str(val['active']) == 'False'):
                    self.peringatan.setText('Pengguna (saya) tidak ditemukan')
                    return
                if(not str(val['hash']) == hashlib.md5(self.myPass.text().encode()).hexdigest()):
                    self.peringatan.setText('Password anda salah')
                    return
                val = database.child('users').child(self.friendID.text()).child('active').get().val()
                print('Out Friend : ' + str(val))
                if(str(val) == 'None'):
                    self.peringatan.setText('Pengguna (teman) tidak ditemukan')
                    return
                elif(str(val) == 'True'):
                    self.loadButton.setText("Disconnect")
                    self.peringatan.setText('Selamat datang, silahkan tuliskan pesan')
                    value = [
                        hashlib.md5(self.friendID.text().encode()).hexdigest(),
                        hashlib.md5(self.myID.text().encode()).hexdigest()
                    ]
                    value.sort()
                    globalVar.hashval = value[0]+value[1]
                    print(globalVar.hashval)
                    globalVar.statusAktif = True
                    threading.Thread(target=self.listening).start()
                else:
                    self.peringatan.setText('Error : ' + str(val))
                    return
        else:
            self.loadButton.setText("Connect")
            globalVar.statusAktif = False
            self.attachState.setEnabled(False)
            self.attachState.setChecked(False)
            self.chatRoom.setText('')
            self.inputBox.setPlainText('')
            self.peringatan.setText('Selamat datang di aplikasi "ChitChatChut"')

        self.buatBaru.setDisabled(globalVar.statusAktif)
        self.myID.setDisabled(globalVar.statusAktif)
        self.myPass.setDisabled(globalVar.statusAktif)
        self.friendID.setDisabled(globalVar.statusAktif)
        self.peringatan_2.setDisabled(globalVar.statusAktif)
        self.peringatan_3.setDisabled(globalVar.statusAktif)
        self.peringatan_4.setDisabled(globalVar.statusAktif)
        self.inputBox.setEnabled(globalVar.statusAktif)
        self.chatRoom.setEnabled(globalVar.statusAktif)
        self.sendButton.setEnabled(globalVar.statusAktif)
        self.attachButton.setEnabled(globalVar.statusAktif)

    def attachCheck(self):
        if(not self.attachState.isChecked() and globalVar.statusAktif):
            self.attachState.setEnabled(False)
            self.attachButton.setEnabled(True)

    def attach(self):
        fname, jenis = QFileDialog.getOpenFileName(self, 'Open file', 
        'c:\\',"All Files (*.*)")
        if(not fname == ''):
            filename = fname.split('/')
            filename = filename[len(filename)-1]
            self.attachButton.setEnabled(False)
            self.attachState.setEnabled(True)
            self.attachState.setChecked(True)
            self.peringatan.setText('File Terpilih : ' + filename)
            globalVar.attach = fname
            globalVar.filename = filename

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    win = mainProgram()
    win.show()
    sys.exit(app.exec_())
