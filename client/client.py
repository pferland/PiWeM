import sys
from PyQt4 import QtGui, QtCore
class Window(QtGui.QMainWindow):

    def __init__(self):
        super(Window, self).__init__()
        self.setGeometry(50, 50, 500, 300)
        self.setWindowTitle("PiWeM QT4 Client")
        #self.setWindowIcon(QtGui.QIcon('pythonlogo.png'))
        self.settings = QtCore.QSettings("MyCompany", "MyApp")

        # Remember last Window Location
        if not self.settings.value("geometry") == None:
            self.restoreGeometry(self.settings.value("geometry"))
        if not self.settings.value("windowState") == None:
            self.restoreState(self.settings.value("windowState"))

        self.ExitAction = QtGui.QAction("&Exit", self)
        self.ExitAction.setShortcut("Ctrl+Q")
        self.ExitAction.setStatusTip('Well, there you go...')
        self.ExitAction.triggered.connect(self.close_application)

        self.ConnectAction = QtGui.QAction("&Connect", self)
        self.ConnectAction.setShortcut("Ctrl+O")
        self.ConnectAction.setStatusTip('Connect to Weather Station.')
        self.ConnectAction.triggered.connect(self.connectToStation)

        self.DisconnectAction = QtGui.QAction("&Disconnect", self)
        self.DisconnectAction.setShortcut("Ctrl+D")
        self.DisconnectAction.setStatusTip('Disconnect from Weather Station.')
        self.DisconnectAction.setDisabled(True)
        self.DisconnectAction.triggered.connect(self.disconnectFromStation)

        mainMenu = self.menuBar()
        fileMenu = mainMenu.addMenu('&File')
        fileMenu.addAction(self.ConnectAction)
        fileMenu.addAction(self.DisconnectAction)
        fileMenu.addAction(self.ExitAction)

        self.statusBar()
        # Show the Window now.
        self.show()

    def closeEvent(self, event):
        self.settings.setValue("geometry", self.saveGeometry())
        self.settings.setValue("windowState", self.saveState())
        super(Window, self).closeEvent(event)

    def close_application(self):
        print("Well there you go smart guy...")
        sys.exit()

    def connectToStation(self):


        print("Connected")
        self.ConnectAction.setDisabled(True)
        self.DisconnectAction.setDisabled(False)


    def disconnectFromStation(self):
        print("Disconnected")
        self.DisconnectAction.setDisabled(True)
        self.ConnectAction.setDisabled(False)


def main():
    app = QtGui.QApplication(sys.argv)
    main = Window()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
