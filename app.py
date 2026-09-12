import json
import sys
import urllib.error
import urllib.request
from pathlib import Path

from PySide6.QtCore import QPoint, QRect, QSettings, Qt, QThread, QTimer, Signal
from PySide6.QtGui import QAction, QIcon, QPainter, QPixmap
from PySide6.QtWidgets import (
    QApplication, QCheckBox, QDialog, QFormLayout, QHBoxLayout, QLabel,
    QLineEdit, QMenu, QMessageBox, QPushButton, QSpinBox, QTextBrowser,
    QTextEdit, QVBoxLayout, QWidget,
)

ROOT = Path(__file__).resolve().parent.parent
SPRITES = ROOT / "assets" / "sprite_sheet.png"


class ApiWorker(QThread):
    done = Signal(str)
    failed = Signal(str)

    def __init__(self, url, key, model, messages):
        super().__init__()
        self.url, self.key, self.model, self.messages = url, key, model, messages

    def run(self):
        try:
            endpoint = self.url.rstrip("/")
            if not endpoint.endswith("/chat/completions"):
                endpoint += "/chat/completions"
            body = json.dumps({"model": self.model, "messages": self.messages,
                               "temperature": 0.8}).encode("utf-8")
            req = urllib.request.Request(endpoint, data=body, method="POST",
                headers={"Content-Type": "application/json",
                         "Authorization": f"Bearer {self.key}"})
            with urllib.request.urlopen(req, timeout=60) as response:
                data = json.loads(response.read().decode("utf-8"))
            self.done.emit(data["choices"][0]["message"]["content"])
        except (urllib.error.URLError, KeyError, ValueError, TimeoutError) as exc:
            self.failed.emit(str(exc))


class SettingsDialog(QDialog):
    def __init__(self, settings, parent=None):
        super().__init__(parent)
        self.settings = settings
        self.setWindowTitle("桌宠设置")
        self.url = QLineEdit(settings.value("ai/base_url", "https://api.openai.com/v1"))
        self.key = QLineEdit(settings.value("ai/api_key", "")); self.key.setEchoMode(QLineEdit.Password)
        self.model = QLineEdit(settings.value("ai/model", "gpt-4.1-mini"))
        self.prompt = QTextEdit(settings.value("ai/prompt", "你是一个温暖、活泼、简洁的中文桌宠伙伴。"))
        self.prompt.setFixedHeight(80)
        self.size = QSpinBox(); self.size.setRange(120, 600); self.size.setValue(int(settings.value("pet/size", 280)))
        self.top = QCheckBox("始终置顶"); self.top.setChecked(settings.value("pet/top", True, type=bool))
        form = QFormLayout(); form.addRow("接口地址", self.url); form.addRow("API Key", self.key)
        form.addRow("模型", self.model); form.addRow("角色设定", self.prompt); form.addRow("桌宠尺寸", self.size); form.addRow("", self.top)
        ok = QPushButton("保存"); cancel = QPushButton("取消"); ok.clicked.connect(self.accept); cancel.clicked.connect(self.reject)
        buttons = QHBoxLayout(); buttons.addStretch(); buttons.addWidget(cancel); buttons.addWidget(ok)
        layout = QVBoxLayout(self); layout.addLayout(form); layout.addLayout(buttons); self.resize(470, 330)

    def accept(self):
        for key, val in [("ai/base_url", self.url.text().strip()), ("ai/api_key", self.key.text().strip()),
                         ("ai/model", self.model.text().strip()), ("ai/prompt", self.prompt.toPlainText().strip()),
                         ("pet/size", self.size.value()), ("pet/top", self.top.isChecked())]: self.settings.setValue(key, val)
        self.settings.sync(); super().accept()


class ChatDialog(QDialog):
    def __init__(self, settings, parent=None):
        super().__init__(parent)
        self.settings, self.history, self.worker = settings, [], None
        self.setWindowTitle("和小桃聊天")
        self.view = QTextBrowser(); self.input = QTextEdit(); self.input.setPlaceholderText("输入消息……"); self.input.setFixedHeight(75)
        send = QPushButton("发送"); send.clicked.connect(self.send)
        layout = QVBoxLayout(self); layout.addWidget(self.view); layout.addWidget(self.input); layout.addWidget(send)
        self.resize(430, 520)

    def send(self):
        text = self.input.toPlainText().strip()
        if not text: return
        key = self.settings.value("ai/api_key", "")
        if not key:
            QMessageBox.information(self, "需要设置", "请先在右键菜单 → 设置中填写 API Key。")
            return
        self.input.clear(); self.view.append(f"<b>你：</b>{text}")
        self.history.append({"role": "user", "content": text})
        msgs = [{"role": "system", "content": self.settings.value("ai/prompt", "你是中文桌宠伙伴。")}] + self.history[-20:]
        self.worker = ApiWorker(self.settings.value("ai/base_url", "https://api.openai.com/v1"), key,
                                self.settings.value("ai/model", "gpt-4.1-mini"), msgs)
        self.worker.done.connect(self.answer); self.worker.failed.connect(lambda e: self.view.append(f"<b>连接失败：</b>{e}")); self.worker.start()

    def answer(self, text):
        self.history.append({"role": "assistant", "content": text}); self.view.append(f"<b>小桃：</b>{text}")


class PetWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.settings = QSettings("PinkHelmetPet", "PinkHelmetPet")
        self.drag_offset, self.frame = None, 0
        self.sheet = QPixmap(str(SPRITES)); self.frames = self.slice_sheet(self.sheet)
        self.timer = QTimer(self); self.timer.timeout.connect(self.next_frame); self.timer.start(180)
        self.apply_settings(first=True)
        pos = self.settings.value("pet/position")
        if pos: self.move(pos)
        else:
            screen = QApplication.primaryScreen().availableGeometry(); self.move(screen.right()-self.width()-25, screen.bottom()-self.height()-25)

    @staticmethod
    def slice_sheet(sheet):
        w, h = sheet.width() // 4, sheet.height() // 2
        return [sheet.copy(QRect(c*w, r*h, w, h)) for r in range(2) for c in range(4)]

    def apply_settings(self, first=False):
        flags = Qt.FramelessWindowHint | Qt.Tool
        if self.settings.value("pet/top", True, type=bool): flags |= Qt.WindowStaysOnTopHint
        self.setWindowFlags(flags); self.setAttribute(Qt.WA_TranslucentBackground)
        size = int(self.settings.value("pet/size", 280)); self.setFixedSize(size, size)
        if not first: self.show()

    def paintEvent(self, event):
        p = QPainter(self); p.setRenderHint(QPainter.SmoothPixmapTransform)
        p.drawPixmap(self.rect(), self.frames[self.frame])

    def next_frame(self):
        self.frame = (self.frame + 1) % len(self.frames); self.update()

    def mousePressEvent(self, e):
        if e.button() == Qt.LeftButton: self.drag_offset = e.globalPosition().toPoint() - self.frameGeometry().topLeft()

    def mouseMoveEvent(self, e):
        if self.drag_offset is not None and e.buttons() & Qt.LeftButton: self.move(e.globalPosition().toPoint() - self.drag_offset)

    def mouseReleaseEvent(self, e):
        if e.button() == Qt.LeftButton:
            self.drag_offset = None; self.settings.setValue("pet/position", self.pos())

    def mouseDoubleClickEvent(self, e):
        if e.button() == Qt.LeftButton: self.open_chat()

    def contextMenuEvent(self, e):
        menu = QMenu(self)
        chat = menu.addAction("AI 对话"); settings = menu.addAction("设置")
        menu.addSeparator(); reset = menu.addAction("重置位置"); quit_action = menu.addAction("退出")
        chosen = menu.exec(e.globalPos())
        if chosen == chat: self.open_chat()
        elif chosen == settings:
            if SettingsDialog(self.settings, self).exec(): self.apply_settings()
        elif chosen == reset:
            screen = QApplication.primaryScreen().availableGeometry(); self.move(screen.right()-self.width()-25, screen.bottom()-self.height()-25)
        elif chosen == quit_action: QApplication.quit()

    def open_chat(self):
        dialog = ChatDialog(self.settings, self); dialog.show(); dialog.raise_(); dialog.exec()


def main():
    app = QApplication(sys.argv); app.setApplicationName("粉盔小桃桌宠"); app.setQuitOnLastWindowClosed(False)
    pet = PetWidget(); pet.show(); sys.exit(app.exec())
