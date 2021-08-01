from PyQt5.QtWidgets import QMessageBox

class DialogTool():
    def dialogQuestion(self, window, info, title = 'Otazka', funcExec = None, funcCancel = None):
        mbox = QMessageBox(window)
        mbox.setWindowTitle(title)
        mbox.setIcon(QMessageBox.Icon.Question)
        mbox.setText(info)
        mbox.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)

        if mbox.exec() == QMessageBox.Ok and funcExec != None : 
            funcExec()
        elif mbox.exec() == QMessageBox.Cancel and funcCancel != None : 
            funcCancel()    
        mbox.show()

    #messageType : 0 = info, 1 = warning
    def dialogInfo(self, window, info, title = 'Info', messageType = 0, funcExec = None):
        mbox = QMessageBox(window)
        mbox.setWindowTitle(title)
        mbox.setIcon( QMessageBox.Icon.Information if messageType == 0 else QMessageBox.Icon.Warning)
        mbox.setText(info)
        mbox.setStandardButtons(QMessageBox.Ok, QMessageBox.Cancel)
        
        if mbox.exec() == QMessageBox.Ok and funcExec != None : funcExec()
        elif mbox.exec() == QMessageBox.Cancel: return
        mbox.show()
