from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWebEngineWidgets import *
from PyQt5.QtWidgets import *
#Settings
theme = "white"


class BrowserEngineView(QWebEngineView):
    tabs = []

    def __init__(self, Main, parent=None):
        super(BrowserEngineView, self).__init__(parent)
        self.mainWindow = Main

    def createWindow(self, windowType):
        webview = BrowserEngineView(self.mainWindow)
        tab = BrowserTab(self.mainWindow)
        tab.browser = webview
        tab.setCentralWidget(tab.browser)
        self.tabs.append(tab)
        self.mainWindow.add_tab(tab)
        return webview


class BrowserTab(QMainWindow):
    def __init__(self, Main, parent=None):
        super(BrowserTab, self).__init__(parent)
        self.mainWindow = Main
        self.browser = BrowserEngineView(self.mainWindow)
        self.browser.load(QUrl("https://www.duckduckgo.com"))
        self.setCentralWidget(self.browser)
        self.navigation_bar = QToolBar('Navigation')
        self.navigation_bar.setIconSize(QSize(16, 16))
        self.navigation_bar.setMovable(False)
        self.addToolBar(self.navigation_bar)
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)

        self.back_button = QAction(QIcon('%s/images/back.png' % theme), 'Back', self)
        self.next_button = QAction(QIcon('%s/images/forward.png' % theme), 'Forward', self)
        self.stop_button = QAction(QIcon('%s/images/stop.png' % theme), 'Stop', self)
        self.refresh_button = QAction(QIcon('%s/images/reload.png' % theme), 'Refresh', self)
        self.home_button = QAction(QIcon('%s/images/home.png' % theme), 'Go home', self)
        self.enter_button = QAction(QIcon('%s/images/search.png' % theme), 'Search', self)
        self.ssl_label1 = QLabel(self)
        self.ssl_label2 = QLabel(self)
        self.url_text_bar = QLineEdit(self)
        self.url_text_bar.setMinimumWidth(300)
        self.progress_bar = QProgressBar()
        self.progress_bar.setMaximumWidth(120)
        self.navigation_bar.addAction(self.back_button)
        self.navigation_bar.addAction(self.next_button)
        self.navigation_bar.addAction(self.stop_button)
        self.navigation_bar.addAction(self.refresh_button)
        self.navigation_bar.addAction(self.home_button)
        self.navigation_bar.addSeparator()
        self.navigation_bar.addWidget(self.ssl_label1)
        self.navigation_bar.addWidget(self.ssl_label2)
        self.navigation_bar.addWidget(self.url_text_bar)
        self.navigation_bar.addAction(self.enter_button)
        self.navigation_bar.addSeparator()
        self.navigation_bar.addWidget(self.progress_bar)
        # self.navigation_bar.addAction(self.set_button)
        def save_page(*a, view=self.browser):
            destination = QFileDialog.getSaveFileName(self, "Save Page")
            print(repr(destination))
            if destination:
                view.page().save(destination[0])

        self.browser.pageAction(
            QWebEnginePage.SavePage
        ).triggered.connect(save_page)

    def navigate_to_url(self):
        s = QUrl(self.url_text_bar.text())
        if s.isValid():
            if s.scheme() == '':
                s.setScheme('http')
            self.browser.load(s)
        else: 
            sg = QUrl("https://duckduckgo.com/%s" % s)
            self.browser.load(sg)


    def navigate_to_home(self):
        s = QUrl("https://www.duckduckgo.com/")
        self.browser.load(s)

    def renew_urlbar(self, s):
        prec = s.scheme()
        if prec == 'http':
            self.ssl_label1.setPixmap(QPixmap("%s/images/unsafe.png" % theme).scaledToHeight(24))
            self.ssl_label2.setText(" This site is unsafe ")
            self.ssl_label2.setStyleSheet("color:red;")
        elif prec == 'https':
            self.ssl_label1.setPixmap(QPixmap("%s/images/safe.png" % theme).scaledToHeight(24))
            self.ssl_label2.setText(" This site is safe ")
            self.ssl_label2.setStyleSheet("color:green;")
        self.url_text_bar.setText(s.toString())
        self.url_text_bar.setCursorPosition(0)

    def renew_progress_bar(self, p):
        self.progress_bar.setValue(p)


class BrowserWindow(QMainWindow):
    name = "Silvercat v.0.1"
    version = "0.1"
    date = "2020.1.26"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        with open("%s/main.qss" % theme,"r") as fh:
            self.setStyleSheet(fh.read())
        self.setWindowTitle('Silvercat v.0.1')
        self.setWindowIcon(QIcon('logo.png'))
        self.resize(1200, 900)
        self.tabs = QTabWidget(
            self, tabsClosable=True, movable=True, elideMode=Qt.ElideRight
        )
        self.add_new = QToolButton(
                self,
                text="+",
                triggered=lambda: print("test"),
                shortcut=QKeySequence.AddTab,
            )
        self.tabs.setCornerWidget(self.add_new)
        self.tabs.setTabShape(0)
        self.setCentralWidget(self.tabs)
        self.tabs.tabCloseRequested.connect(self.close_current_tab)
        self.tabs.currentChanged.connect(lambda i: self.setWindowTitle(self.tabs.tabText(i) + " - " + self.name))
        self.add_new_tab()

    def add_new_tab(self):
        new = BrowserTab(self)
        new.browser.load(QUrl("https://www.duckduckgo.com/"))
        self.add_tab(new)

    def add_tab(self, tab):
        i = self.tabs.addTab(tab, "Untitled")
        self.tabs.setCurrentIndex(i)
        print(i)
        tab.back_button.triggered.connect(tab.browser.back)
        print(i)
        tab.next_button.triggered.connect(tab.browser.forward)
        print(i)
        tab.stop_button.triggered.connect(tab.browser.stop)
        print(i)
        tab.refresh_button.triggered.connect(tab.browser.reload)
        print(i)
        tab.home_button.triggered.connect(tab.navigate_to_home)
        print(i)
        print(i)
        print(i)
        tab.url_text_bar.returnPressed.connect(tab.navigate_to_url)
        print(i)
        tab.browser.urlChanged.connect(lambda: tab.back_button.setEnabled(tab.browser.page().history().canGoBack()))
        tab.browser.urlChanged.connect(lambda: tab.next_button.setEnabled(tab.browser.page().history().canGoForward()))
        tab.browser.page().linkHovered.connect(
            lambda l: tab.statusBar().showMessage(l, 3000)
        )
        tab.browser.urlChanged.connect(tab.renew_urlbar)
        print(i)
        tab.browser.loadProgress.connect(tab.renew_progress_bar)
        print(i)
        tab.browser.titleChanged.connect(lambda title: (self.tabs.setTabText(i, title),
                                                        self.tabs.setTabToolTip(i, title),
                                                        self.setWindowTitle(self.tabs.tabText(i) + " - " + self.name)))
        print(i)
        #tab.browser.iconChanged.connect(self.tabs.setTabIcon(i, tab.browser.icon()))

    def close_current_tab(self, i):
        if self.tabs.count() > 1:
            self.tabs.removeTab(i)
        else:
            self.close()