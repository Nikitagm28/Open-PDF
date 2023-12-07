import sys
import fitz
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog, QGraphicsView, QGraphicsScene, QPushButton, QVBoxLayout, QWidget
from PyQt5.QtGui import QPixmap, QImage, QPen, QColor
from PyQt5.QtCore import Qt, QRectF
from PyQt5.QtWidgets import QGraphicsScene
from PyQt5.QtGui import QBrush
from PyQt5.QtWidgets import QHBoxLayout

class PDFViewer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.rectangles = {} 
        self.initUI()
        
    def initUI(self):
        self.setWindowTitle('Open PDF')
        self.setGeometry(100, 100, 800, 600)
        
        # Создание кнопок
        self.loadPdfButton = QPushButton('Загрузить', self)
        self.prevPageButton = QPushButton('<', self)
        self.nextPageButton = QPushButton('>', self)

        self.loadPdfButton.clicked.connect(self.loadPdf)
        self.prevPageButton.clicked.connect(self.prevPage)
        self.nextPageButton.clicked.connect(self.nextPage)

        topLayout = QHBoxLayout()
        topLayout.addWidget(self.loadPdfButton)
        topLayout.addStretch()  
        topLayout.addWidget(self.prevPageButton)
        topLayout.addWidget(self.nextPageButton)

        mainLayout = QVBoxLayout()
        mainLayout.addLayout(topLayout) 
        self.view = QGraphicsView(self)
        self.scene = CustomGraphicsScene(self)
        self.view.setScene(self.scene)
        mainLayout.addWidget(self.view)  

        centralWidget = QWidget()
        centralWidget.setLayout(mainLayout)
        self.setCentralWidget(centralWidget)

        self.pdf_document = None
        self.current_page = 0


    def loadPdf(self):
        path, _ = QFileDialog.getOpenFileName(self, "Открыть файл", "", "PDF files (*.pdf)")
        if path:
            self.pdf_document = fitz.open(path)
            self.current_page = 0
            self.displayPage(self.current_page)

    def displayPage(self, page_number):
        if self.pdf_document:
            page = self.pdf_document.load_page(page_number)
            pix = page.get_pixmap()
            img = QImage(pix.samples, pix.width, pix.height, pix.stride, QImage.Format_RGB888)
            pixmap = QPixmap.fromImage(img)
            self.scene.clear()
            self.scene.addPixmap(pixmap)
            self.drawSavedRectangles(page_number)

    def prevPage(self):
        if self.pdf_document and self.current_page > 0:
            self.current_page -= 1
            self.displayPage(self.current_page)

    def nextPage(self):
        if self.pdf_document and self.current_page < self.pdf_document.page_count - 1:
            self.current_page += 1
            self.displayPage(self.current_page)

    def drawSavedRectangles(self, page_number):
        if page_number in self.rectangles:
            for rect in self.rectangles[page_number]:
                self.scene.addRect(rect, QPen(QColor(Qt.red)), QBrush(Qt.NoBrush))

class CustomGraphicsScene(QGraphicsScene):
    def __init__(self, parent=None):
        super(CustomGraphicsScene, self).__init__(parent)
        self.rectangles = {}
        self.start = None
        self.end = None
        self.current_rect = None

    def mousePressEvent(self, event):
        self.start = event.scenePos()
        pen = QPen(QColor(Qt.red))
        pen.setWidth(2)
        brush = QBrush(Qt.NoBrush)
        self.current_rect = self.addRect(QRectF(self.start, self.start), pen, brush)
        event.accept()

    def mouseMoveEvent(self, event):
        if self.start is not None:
            self.end = event.scenePos()
            rect = QRectF(self.start, self.end).normalized()
            self.current_rect.setRect(rect)
        event.accept()

    def mouseReleaseEvent(self, event):
        if self.start is not None and self.end is not None:
            rect = QRectF(self.start, self.end).normalized()
            self.current_rect.setRect(rect)
            if self.parent().current_page not in self.parent().rectangles:
                self.parent().rectangles[self.parent().current_page] = []
            self.parent().rectangles[self.parent().current_page].append(rect)
        self.start = None
        self.end = None
        event.accept()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    viewer = PDFViewer()
    viewer.show()
    sys.exit(app.exec_())