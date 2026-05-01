import sys
import fitz
import PyPDF2

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout,
    QPushButton, QFileDialog, QLabel, QScrollArea,
    QFrame, QHBoxLayout
)
from PySide6.QtGui import QPixmap, QImage
from PySide6.QtCore import Qt


class PDFEditor(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("PDF Editor Pro")
        self.setGeometry(200, 100, 1100, 750)

        self.pages = []
        self.previews = []

        # ---------------- ROOT UI ----------------
        central = QWidget()
        self.setCentralWidget(central)

        layout = QVBoxLayout(central)

        self.load_btn = QPushButton("📂 Load PDF")
        self.load_btn.clicked.connect(self.load_pdf)

        self.merge_btn = QPushButton("➕ Merge PDFs")
        self.merge_btn.clicked.connect(self.merge_pdfs)

        self.save_btn = QPushButton("💾 Save PDF")
        self.save_btn.clicked.connect(self.save_pdf)

        layout.addWidget(self.load_btn)
        layout.addWidget(self.merge_btn)
        layout.addWidget(self.save_btn)

        # ---------------- SCROLL AREA ----------------
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)

        self.container = QWidget()
        self.scroll_layout = QVBoxLayout(self.container)

        self.scroll.setWidget(self.container)
        layout.addWidget(self.scroll)

    # ---------------- LOAD ----------------
    def load_pdf(self):
        path, _ = QFileDialog.getOpenFileName(self, "Open PDF", "", "PDF Files (*.pdf)")
        if not path:
            return

        self.pages = list(PyPDF2.PdfReader(path).pages)
        self.previews = self.render_previews(path, len(self.pages))

        self.refresh()

    # ---------------- MERGE ----------------
    def merge_pdfs(self):
        paths, _ = QFileDialog.getOpenFileNames(self, "Merge PDFs", "", "PDF Files (*.pdf)")
        if not paths:
            return

        for path in paths:
            reader = PyPDF2.PdfReader(path)
            pages = list(reader.pages)

            self.pages.extend(pages)
            self.previews.extend(self.render_previews(path, len(pages)))

        self.refresh()

    # ---------------- SAVE ----------------
    def save_pdf(self):
        path, _ = QFileDialog.getSaveFileName(self, "Save PDF", "", "PDF Files (*.pdf)")
        if not path:
            return

        writer = PyPDF2.PdfWriter()

        for page in self.pages:
            writer.add_page(page)

        with open(path, "wb") as f:
            writer.write(f)

    # ---------------- PREVIEWS ----------------
    def render_previews(self, path, count):
        doc = fitz.open(path)
        previews = []

        for i in range(count):
            page = doc.load_page(i)
            pix = page.get_pixmap()

            img = QImage(
                pix.samples,
                pix.width,
                pix.height,
                pix.stride,
                QImage.Format_RGB888
            )

            pixmap = QPixmap.fromImage(img).scaledToWidth(180, Qt.SmoothTransformation)
            previews.append(pixmap)

        doc.close()
        return previews

    # ---------------- UI ----------------
    def refresh(self):
        # clear UI
        for i in reversed(range(self.scroll_layout.count())):
            widget = self.scroll_layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()

        # rebuild pages
        for i in range(len(self.pages)):
            self.add_page(i)

    def add_page(self, i):
        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background-color: #2b2b2b;
                border-radius: 12px;
                padding: 10px;
                margin: 5px;
            }
        """)

        layout = QHBoxLayout(card)

        # Preview
        img = QLabel()
        img.setPixmap(self.previews[i])

        # Page label
        label = QLabel(f"Page {i + 1}")
        label.setStyleSheet("color: white; font-size: 14px;")

        # Buttons
        up_btn = QPushButton("⬆")
        down_btn = QPushButton("⬇")
        del_btn = QPushButton("🗑")

        up_btn.clicked.connect(lambda _, i=i: self.move_up(i))
        down_btn.clicked.connect(lambda _, i=i: self.move_down(i))
        del_btn.clicked.connect(lambda _, i=i: self.delete(i))

        layout.addWidget(img)
        layout.addWidget(label)
        layout.addWidget(up_btn)
        layout.addWidget(down_btn)
        layout.addWidget(del_btn)

        self.scroll_layout.addWidget(card)

    # ---------------- EDIT FUNCTIONS ----------------
    def move_up(self, i):
        if i <= 0:
            return
        self.swap(i, i - 1)

    def move_down(self, i):
        if i >= len(self.pages) - 1:
            return
        self.swap(i, i + 1)

    def swap(self, i, j):
        self.pages[i], self.pages[j] = self.pages[j], self.pages[i]
        self.previews[i], self.previews[j] = self.previews[j], self.previews[i]
        self.refresh()

    def delete(self, i):
        del self.pages[i]
        del self.previews[i]
        self.refresh()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PDFEditor()
    window.show()
    sys.exit(app.exec())