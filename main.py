from flask import Flask, render_template, url_for, redirect, request
from flask_sqlalchemy import SQLAlchemy
#from sqlalchemy import func
import os
from translit import translit ##Функция для перевода в транслит
from update import update_creation_name ##Функция для преобразования в корректное имя среди папок

##Конфигурация
SECRET_KEY = "ce9045c1ff69baa07aace63b62b87fb3be532eace035fbae804b0fea52d31923f903b2a2859f73bb4d51dbd612f72d9715e6"

##WSGI-приложение
app = Flask(__name__)
app.config.from_object(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///data.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

##База данных
db = SQLAlchemy(app)

##Таблица с писателями
class Writers(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    writer_name = db.Column(db.String(100), nullable=False)
    writer_url = db.Column(db.String(120), nullable=False)

    def __repr__(self):
        return f"<{self.id}: {self.writer_name}: {self.writer_url}>"

##Таблица с произведениями (книгами в основном, поэтому Books)
class Books(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    writer_name = db.Column(db.String(100), nullable=False)
    book_name = db.Column(db.String(150), nullable=False)
    book_url = db.Column(db.String(120), nullable=False)
    book_text = db.Column(db.Text, nullable=False)

    def __repr__(self):
        return f"<{self.id}: {self.writer_name}-{self.book_name}>"

##Главная страница со всеми писателями
@app.route("/", methods=["POST", "GET"])
def index():

    writers = Writers.query.all()

    ##Обработка POST запроса (поиск писателя)
    if request.method == "POST":
        writers_list = [] ##Для удобства и вообще корректности перебросим все объекты бд в список и работать далее будем с ним
        new_writers = [] ##Список с новыми писателями для отображения по результатам поиска
        writer_name_search = request.form["writer_name_search"].strip().title() ##Имя писателя из формы (без пробелов и с заглавными Имя-Фамилия)
        
        ##
        for name in writers:
            writers_list.append(name) ##Добавляем элемент бд в список

        ##
        for i in writers_list: ##Здесь будем добавлять элементы списка в новый список писателей, запрошенных пользователем
            if writer_name_search in str(i): ##Если ищущийся писатель внутри объекта i
                new_writers.append(i)  ##Добавляем i в список новых писателей

        return render_template("index.html", title="Главная", writers=new_writers)  ##Отображаем с новыми писателями

    return render_template("index.html", title="Главная", writers=writers)

##Обработчик страницы с писателем
@app.route("/writer/<translit_name>")
def page_writer(translit_name):
    writer_name = Writers.query.filter_by(writer_url="/"+translit_name).first().writer_name
    books = Books.query.filter_by(writer_name=writer_name).order_by(db.func.length(Books.book_name).desc()).all()

    return render_template("writer.html",
     title=writer_name,
     writer_name=writer_name,
     books=books,
     translit_name=translit_name)

##Обработчик страницы с произведением и разделами (главами)
@app.route("/writer/<writer>/creation/<translit_creation_name>")
def page_creation(writer, translit_creation_name):

    ##Берём имена произведения и имя автора
    creation_name = Books.query.filter_by(book_url="/"+translit_creation_name).first().book_name.strip()
    writer_name = Books.query.filter_by(book_name=creation_name).first().writer_name.strip()

    text_creation = Books.query.filter_by(book_name=creation_name).first().book_text.strip() ##Текст перед главами
    
    ##Для исключения невозможных символов в названии папки
    creation_name_search = update_creation_name(creation_name)
    
    ##Заполняем главы в список; Глав меньше одного или всего одна - отдаём пустой список глав, т.к. текст коротких произведений будет храниться в БД
    chapters = []
    if os.path.exists(app.root_path + f"/static/txt/{writer_name}/{creation_name_search}"):
        if len(os.listdir(app.root_path + f"/static/txt/{writer_name}/{creation_name_search}")) <= 1:
            chapters = []
        else:
            chapters = [ch[3:-4] for ch in os.listdir(app.root_path + f"/static/txt/{writer_name}/{creation_name_search}")]

    #.replace("Ɂ", "?").replace("꞉", ":")

    return render_template(
        "creation.html",
         title=creation_name,
         chapters=chapters,
         creation_name=creation_name,
         writer_name=writer_name,
         translit_creation_name=translit_creation_name,
         writer=writer,
         text_creation=text_creation)

##Обработчик страницы с содержанием произведения
@app.route("/writer/<writer>/creation/<translit_creation_name>/<chapter>")
def page_creation_content(writer, translit_creation_name, chapter):

    ##Убираем неккоректные знаки для верного поиска файлов внутри системы по папкам
    if "?" in chapter:
        chapter = chapter.replace("?", "")


    creation_name = Books.query.filter_by(book_url="/"+translit_creation_name).first().book_name.strip() ##Имя произведения
    creation_name_search = update_creation_name(creation_name).strip() ##Имя произведения для поиска по папкам
    writer_name = Books.query.filter_by(book_name=creation_name).first().writer_name.strip() ## Имя автора
    chapters = [] ##Тут будут главы для вставки их вверх и низ блока с контентом

    if os.path.exists(app.root_path + f"/static/txt/{writer_name}/{creation_name_search}"):
        chapters = [ch[3:-4] for ch in os.listdir(app.root_path + f"/static/txt/{writer_name}/{creation_name_search}")] ##Выбираем в список название главы по имени файла с третьего индекса по -4 (точка перед расширением txt)
    text = "" ##Здесь будет текст
    ##Скрипт для выборки файла главы с текстом по имени главы в url. Поскольку названия файлов начинаются с 01_ и т.д.
    try:
        for file_n in os.listdir(app.root_path + f"/static/txt/{writer_name}/{creation_name_search}"):
            if chapter in [file_n[3:-4]]:
                with open(app.root_path + f"/static/txt/{writer_name}/{creation_name_search}/{file_n}", "r") as file:
                    text = file.read()
    except UnicodeDecodeError:
        for file_n in os.listdir(app.root_path + f"/static/txt/{writer_name}/{creation_name_search}"):
            if chapter in [file_n[3:-4]]:
                with open(app.root_path + f"/static/txt/{writer_name}/{creation_name_search}/{file_n}", "r", encoding="utf-8") as file:
                    text = file.read()

    return render_template("creation_content.html",
     text_content=text,
     chapters=chapters,
     translit_creation_name=translit_creation_name,
     writer=writer,
     active_chapter=chapter,
     creation_name=creation_name
     )

if __name__ == "__main__":
    app.run("localhost", debug=True)

#http://192.168.0.102:5000/