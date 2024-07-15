# подключение библиотек
from PyQt5 import QtMultimedia
from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtGui import QPixmap
from sys import argv, exit
from interface import *
import json as js
from random import randint
from os.path import exists

"""Создаём переменную для хранения наших вопросов с ответами"""
question_dict = None

class Frontend(Ui_MainWindow, QMainWindow):

    COUNT_QUESTION = 4 # кол-во вопросов

    def __init__(self):
        """Инициализируем класс для дальнейшей работы с формой"""
        super().__init__() # передаём значения функции __init__ из родительского класса
        self.setupUi(self)
        self.bank_q = list(map(int, question_dict.keys())) # создаём список, в котором хранятся номера вопрос из словаря
        """ так как главное меню будет открываться несколько раз с обнулением некоторых
            переменных, то она была выведена в отдельную функцию"""
        self.createMenu()

    def setupUi(self, MainWindow):
        """ функция для работы с компонентами формы"""
        super().setupUi(self) # передаём значения функции setupUi из родительского класса
        self.exit_app.clicked.connect(lambda: exit(app.exec_()))
        self.start_test.clicked.connect(self.startTest)
        self.next.clicked.connect(self.createQuestion)
        self.end_btn.clicked.connect(self.createMenu)
        self.video_start.clicked.connect(lambda: self.btn_video(r"resourse/presentation/1.avi"))
        self.end_video.clicked.connect(self.endVideo)
        self.show_mistake.clicked.connect(lambda: self.mistake())
        self.to_rez.clicked.connect(lambda: self.test_stacked.setCurrentWidget(self.rezult))
        self.up.clicked.connect(lambda: self.mistake('next'))
        self.down.clicked.connect(lambda: self.mistake('back'))
        self.play.clicked.connect(lambda: self.media.play())
        self.pause.clicked.connect(lambda: self.media.pause())


    def mistake(self, cmd = 'show'):
        """Функция для вывода ошибок, допущенных в тесте"""
        if len(self.list_mistake) == 0:
            return
        if cmd == 'show':
            """переход на страницу просмотра"""
            self.test_stacked.setCurrentWidget(self.page_mistake)
        elif cmd == 'next':
            """просмотр следующей ошибки"""
            if self.index < len(self.list_mistake) - 1:
                self.index += 1
        elif cmd == 'back':
            """просмотр предыдущей ошибки"""
            if self.index > 0:
                self.index -= 1
        self.mistake_q.setText(self.list_mistake[self.index][0])
        self.you_answer.setText(self.list_mistake[self.index][1])
        self.true_answer.setText(self.list_mistake[self.index][2])

    def endVideo(self):
        '''Выход из страницы видео контента'''
        self.media.stop()
        self.main_stacked.setCurrentWidget(self.main)

    def btn_video(self, url):
        """ Функция для вывода видео-презентации"""
        if not exists(fr'.\{url}'):
            return
        url = QtCore.QUrl(url) # создаём объект пути к видеофайлу
        self.main_stacked.setCurrentWidget(self.video) # переход на страницу, где будет воспроизводиться видео
        self.media = QtMultimedia.QMediaPlayer(self) # создание объекта для видео
        self.media.setVideoOutput(self.show_video) # передаём media объект для вывода видео
        self.media.setMedia(QtMultimedia.QMediaContent(url)) # передаём media путь к необходимому видео
        self.media.play() # воспроизведение видео

    def createMenu(self):
        self.main_stacked.setCurrentWidget(self.main) # переход на страницу главного меню
        """ обнуление переменных для прохождения теста"""
        self.used_q = [] # список уже используемых вопросов
        self.num = 0 # счётчик уже пройденных вопросов
        self.true_a = 0 # счётчик кол-ва правильно отвеченных вопросов
        self.list_mistake = [] # список, допущенных ошибок
        self.index = 0 # позиция, просматриваемой ошибки

    def endTest(self):
        """ Вывод результата прохождения теста"""
        self.test_stacked.setCurrentWidget(self.rezult) # переход на страницу результата
        """ вывод результатов"""
        self.answer.setText(str(self.true_a))
        self.false_answer.setText(str(self.COUNT_QUESTION-self.true_a))

    def checkAnswer(self):
        """ Проверка ответа тестируемого"""
        btn = self.ans_radio.checkedButton() # принимаем ответ тестируемого
        if btn != None and self.num != 0:  # исключаем ответ перед формированием первого вопроса
            # сравнение ответа тестируемого с правильным ответом
            if btn.objectName()[-1] == question_dict.get(num_q).get("true"):
                self.true_a += 1
            else:
                temp = question_dict.get(num_q).get("true")
                self.list_mistake.append([question_dict.get(num_q).get("question"),
                                          btn.text(),
                                          question_dict.get(num_q).get('answers').get(temp)])
            return True
        return False

    def createQuestion(self):
        """ Формирование вопросов"""
        global num_q # Глобальная переменная номера текущего вопроса из банка вопросов
        if (not(self.checkAnswer()) and self.num != 0):
            return
        if self.num < self.COUNT_QUESTION:
            self.num += 1 # номер текущего вопроса
            # избегаем повторения вопроса
            while True:
                # Выбираем случайным образом вопрос из банка вопросов
                num_q = str(randint(min(self.bank_q), max(self.bank_q)))
                if question_dict.get(num_q, False) and not(num_q in self.used_q):
                    # проверка выбранного вопроса на повторение и его наличие в банке
                    self.used_q.append(num_q) # добавляем в список использованных вопросов
                    break
            self.q_num.setText(str(self.num))
            # вставляем картинку и масштабируем его по ширине окно вывода картинки
            self.img.setPixmap(QPixmap(fr"resourse\img\{num_q}.png").scaledToWidth(self.img.width()))
            self.question.setText(question_dict.get(num_q).get("question"))
            # Отключение выделения кнопок
            self.ans_radio.setExclusive(False)
            for i, btn in enumerate(self.ans_radio.buttons()):
                 # выводим предложенные ответы к вопросу
                btn.setChecked(False)
                btn.setText(question_dict.get(num_q).get("answers").get(str(i + 1)))
            self.ans_radio.setExclusive(True)
        else:
             # когда тестируемый ответил на необходимое кол-во вопросов выводим результат прохождения
            self.endTest()


    def startTest(self):
         # переходим на страницу теста и создание первого вопроса
        self.main_stacked.setCurrentWidget(self.test)
        self.test_stacked.setCurrentWidget(self.questions)
        self.createQuestion()


def create_dict():
    """Эта процедура переносит вопросы из файла в переменную
       question_dict в виде словаря."""
    global question_dict
    with open(r"resourse\question.json", 'r', encoding="utf-8") as f:
        question_dict = js.load(f)

if __name__ == '__main__':
    create_dict()
    app = QtWidgets.QApplication(argv)
    win = Frontend()
    win.show()
    exit(app.exec_())