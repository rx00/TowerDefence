from PyQt5.QtWidgets import QAbstractButton
from PyQt5.QtGui import QPainter, QPixmap
from PyQt5.QtCore import pyqtSignal


class ImageButton(QAbstractButton):
    def __init__(self, pixmap, parent=None):
        """
        :param pixmap: ссылка на картинку кнопки
        :param parent: ссылка на объект-прародитель
        :return: объект кнопки
        """
        super(ImageButton, self).__init__(parent)
        self.pixmap = QPixmap(pixmap)

    def change_image(self, pixmap):
        self.pixmap = QPixmap(pixmap)
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.drawPixmap(event.rect(), self.pixmap)

    def sizeHint(self):
        return self.pixmap.size()


class HoverImageButton(ImageButton):
    mouseHover = pyqtSignal(bool)

    def __init__(self, pixmap, parent):
        super(HoverImageButton, self).__init__(pixmap, parent)
        self.setMouseTracking(True)

    def enterEvent(self, event):
        self.mouseHover.emit(True)

    def leaveEvent(self, event):
        self.mouseHover.emit(False)


def register_button(coords, image_list, app_link, run_method_link, args=None):
    """
    :param coords: кортеж координат кнопки (x, y)
    :param image_list: список изображений кнопки, 2 - статика + клик, 3 + hover
    :param app_link: ссылка на объект отрисовки (окно/виджет/итд)
    :param run_method_link: ссылка на объект вызова этой кнопкой
    :return: ссылка на кнопку
    """
    button_images = image_list

    def create_object(coord, app, run_method):

        if len(button_images) == 3:
            button_object = HoverImageButton(button_images[0], app)

            def hover(boolean):
                if boolean:
                    button_object.change_image(button_images[2])
                else:
                    button_object.change_image(button_images[0])

            button_object.mouseHover.connect(hover)
        elif len(button_images) == 2:
            button_object = ImageButton(button_images[0], app)
        else:
            raise ValueError("Ожидается список из 2 или 3 элементов!")

        def pressed():
            button_object.change_image(button_images[1])

        button_object.move(*coord)

        button_object.clicked.connect(pressed)
        button_object.clicked.connect(run_method)
        return button_object

    return create_object(coords, app_link, run_method_link)
