from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWebEngineWidgets import *
from PyQt5.QtWidgets import *

import ctypes
import sqlite3
import os

myappid = u'Pyser.Watercat.Browser.0.1' # arbitrary string
ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

DEBUG_PORT = '5588'
DEBUG_URL = 'http://127.0.0.1:%s' % DEBUG_PORT
os.environ['QTWEBENGINE_REMOTE_DEBUGGING'] = DEBUG_PORT
#Settings
theme = "dark"

program_dir = os.path.dirname(os.path.abspath(__file__)) + '/'
home = QUrl.fromLocalFile(program_dir + "html/home.html")
print(program_dir)

#SQLite
conn = sqlite3.connect('browser.db')
cur = conn.cursor()
cur.execute('''CREATE TABLE if not exists history (
    id INT AUTO_INCREMENT,
    title VARCHAR (255) NOT NULL,
    url VARCHAR (255) NOT NULL,
    PRIMARY KEY (id)
);'''
)
conn.commit()
conn.close()

#Web Browser Viewer
class BrowserEngineView(QWebEngineView):
    tabs = []

    def __init__(self, Main, tab, parent=None):
        super(BrowserEngineView, self).__init__(parent)
        self.settings().setAttribute(
                    QWebEngineSettings.ErrorPageEnabled, False)
        self.tab = tab
        self.mainWindow = Main

    def createWindow(self, windowType):
        tab = BrowserTab(self.mainWindow)
        webview = BrowserEngineView(self.mainWindow, tab)
        tab.browser = webview
        tab.setCentralWidget(tab.browser)
        self.tabs.append(tab)
        self.mainWindow.add_tab(tab)
        return webview
    def contextMenuEvent(self, event):
        self.menu = QMenu("Context menu")
        self.menu.addAction(self.tab.back_button)
        self.menu.addAction(self.tab.reload_button)
        self.menu.addAction(self.tab.browser.pageAction(QWebEnginePage.ReloadAndBypassCache))
        self.menu.addAction(self.tab.next_button)
        self.menu.addSeparator()
        self.menu.addAction(self.tab.browser.pageAction(QWebEnginePage.SavePage))
        self.menu.addSeparator()
        self.menu.addAction(self.tab.browser.pageAction(QWebEnginePage.SelectAll))
        self.menu.popup(event.globalPos())

#Web Browser Tab
class BrowserTab(QMainWindow):
    def __init__(self, Main, parent=None):
        super(BrowserTab, self).__init__(parent)
        self.mainWindow = Main
        self.browser = BrowserEngineView(self.mainWindow, self)
        self.inspectorwin = QDockWidget("Web Inspector", self)
        self.inspector = QWebEngineView()
        self.browser.page().setDevToolsPage(self.inspector.page())
        self.inspector.setWindowTitle('Web Inspector')
        self.inspector.load(QUrl(DEBUG_URL))
        self.inspectorwin.setWidget(self.inspector)
        self.setCentralWidget(self.browser)
        self.navigation_bar = QToolBar('Navigation')
        self.navigation_bar.setIconSize(QSize(16, 16))
        self.navigation_bar.setMovable(False)
        self.addToolBar(self.navigation_bar)
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        
        self.back_button = QAction(QIcon('%s/images/back.png' % theme), 'Back', self)
        self.next_button = QAction(QIcon('%s/images/forward.png' % theme), 'Forward', self)
        self.reload_button = QAction(QIcon('%s/images/reload.png' % theme), 'Refresh', self)
        self.home_button = QAction(QIcon('%s/images/home.png' % theme), 'Go home', self)
        self.enter_button = QAction(QIcon('%s/images/search.png' % theme), 'Search', self)
        self.ssl_label1 = QLabel(self)
        self.ssl_label2 = QLabel(self)
        self.inspect_button = QAction(QIcon('%s/images/inspect.png' % theme), 'Inspect this page', self)
        self.url_text_bar = QLineEdit(self)
        self.url_text_bar.setPlaceholderText("Search with DuckDuckGo or enter a url")
        self.url_text_bar.setMinimumWidth(300)
        self.progress_bar = QProgressBar()
        self.progress_bar.setMaximumWidth(120)
        self.back_button.triggered.connect(self.browser.back)        
        self.next_button.triggered.connect(self.browser.forward)              
        self.reload_button.triggered.connect(self.browser.reload)        
        self.home_button.triggered.connect(self.navigate_to_home)
        self.inspect_button.triggered.connect(
            lambda: self.addDockWidget(Qt.RightDockWidgetArea, self.inspectorwin)
        )   
        self.url_text_bar.returnPressed.connect(self.navigate_to_url)
        
        self.navigation_bar.addAction(self.back_button)
        self.navigation_bar.addAction(self.reload_button)
        self.navigation_bar.addAction(self.next_button)
        self.navigation_bar.addAction(self.home_button)
        self.navigation_bar.addSeparator()
        self.navigation_bar.addWidget(self.ssl_label1)
        self.navigation_bar.addWidget(self.ssl_label2)
        self.navigation_bar.addWidget(self.url_text_bar)
        self.navigation_bar.addAction(self.enter_button)
        self.navigation_bar.addSeparator()
        self.navigation_bar.addAction(self.inspect_button)
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
        url = self.url_text_bar.text()
        qurl = QUrl.fromUserInput(url)
        if qurl.isValid():
            if qurl.scheme() == '':
                qurl.setScheme('http')
            self.browser.load(qurl)
        else: 
            qurl = QUrl("https://duckduckgo.com/?q=%s" % url)
            self.browser.load(qurl)

    def navigate_to_home(self):
        s = home
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
        if s == home:
            self.url_text_bar.setText('')
            self.url_text_bar.setFocus()
        else:
            self.url_text_bar.setText(s.toString())
        self.url_text_bar.setCursorPosition(0)

    def renew_progress_bar(self, p):
        self.progress_bar.setValue(p)

#Web Browser Main Window
class BrowserWindow(QMainWindow):
    name = "Silvercat v.0.1"
    version = "0.1"
    date = "2020.1.26"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if theme != "default":
            with open("%s/main.qss" % theme,"r") as fh:
                self.setStyleSheet(fh.read())
        self.setWindowTitle('Silvercat v.0.1')
        self.resize(1200, 900)
        self.tabs = QTabWidget(
            self, tabsClosable=True, movable=True, elideMode=Qt.ElideRight
        )
        self.add_new = QToolButton(
                self,
                text="+",
                shortcut=QKeySequence.AddTab,
            )
        self.add_new.clicked.connect(self.add_new_tab)
        self.tabs.setCornerWidget(self.add_new)
        self.tabs.setTabShape(0)
        self.setCentralWidget(self.tabs)
        self.tabs.tabCloseRequested.connect(self.close_current_tab)
        self.tabs.currentChanged.connect(lambda i: self.setWindowTitle(self.tabs.tabText(i) + " - " + self.name))
        self.full_screen_action = QAction(
            "Full Screen", self, checkable=True, shortcut=QKeySequence.FullScreen
        )
        self.add_new_tab()

    def add_new_tab(self):
        new = BrowserTab(self)
        new.navigate_to_home()
        self.add_tab(new)


    def add_tab(self, tab):
        self.tab = tab
        i = self.tabs.addTab(tab, "Untitled")
        self.tabs.setCurrentIndex(i)
        self.tab.browser.urlChanged.connect(lambda: self.tab.back_button.setEnabled(self.tab.browser.page().history().canGoBack()))
        self.tab.browser.urlChanged.connect(lambda: self.tab.next_button.setEnabled(self.tab.browser.page().history().canGoForward()))
        self.tab.browser.page().linkHovered.connect(
            lambda l: self.tab.statusBar().showMessage(l, 3000)
        )
        self.tab.browser.loadStarted.connect(lambda: self.tab.reload_button.triggered.connect(self.tab.browser.stop))
        self.tab.browser.loadStarted.connect(lambda: self.tab.reload_button.setIcon(QIcon('%s/images/stop.png' % theme)))
        self.tab.browser.loadFinished.connect(lambda: self.tab.reload_button.triggered.connect(self.tab.browser.reload))
        self.tab.browser.loadFinished.connect(lambda: self.tab.reload_button.setIcon(QIcon('%s/images/reload.png' % theme)))
        self.tab.browser.urlChanged.connect(self.tab.renew_urlbar)
        self.tab.browser.loadProgress.connect(self.tab.renew_progress_bar)
        self.tab.browser.titleChanged.connect(lambda title: (self.tabs.setTabText(i, title),
                                                        self.tabs.setTabToolTip(i, title),
                                                        self.setWindowTitle(self.tabs.tabText(i) + " - " + self.name)))
        self.tab.browser.iconChanged.connect(lambda: self.tabs.setTabIcon(i, self.tab.browser.icon()))
        self.tab.browser.loadFinished.connect(lambda: self.tabs.setTabIcon(i, self.tab.browser.icon()))
        return self.tab
    def add_to_history(title, url):
        conn = sqlite3.connect('browser.db')
        conn.execute('''INSERT INTO history (url, title) 
        VALUES (%s, %s)'''%(title, url));

    def close_current_tab(self, i):
        if self.tabs.count() > 1:
            self.tabs.removeTab(i)
        else:
            self.close()
