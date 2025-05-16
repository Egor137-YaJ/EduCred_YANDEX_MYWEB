from reportlab.lib.pagesizes import landscape, A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.utils import simpleSplit
from datetime import datetime
import os
import uuid
import hashlib


# функция для генерации уникального токена сертификата
def tokenize():
    return str(uuid.uuid4())


# функция, хеширующая имя файла для хранения
def hash_name(st, co, un_t):
    raw = f"{st}_{co}_{un_t}"
    hash_obj = hashlib.sha256(raw.encode('utf-8'))
    return hash_obj.hexdigest()


# функция для генерации сертификатов
def pdf_creating(student_nsp, course_title, univer_title, start_date, end_date, univer_boss, token, mark="—",
                 type="course", logo_path='static/images/EduCred_logo_rb.png'):
    os.makedirs('static/achievements', exist_ok=True)

    # генерация хешированного названия для файла
    clean_student = student_nsp.replace(' ', '_')
    clean_course = course_title.replace(' ', '_')
    filename_only = f"cert_{hash_name(clean_student, clean_course, univer_title)}.pdf"
    full_path = os.path.join('static/achievements', filename_only)
    short_path = os.path.join('achievements', filename_only).replace('\\', '/')

    # подключение шрифтов
    pdfmetrics.registerFont(TTFont('DejaVuSans', 'static/fonts/DejaVuSans.ttf'))
    pdfmetrics.registerFont(TTFont('DejaVuSans-Bold', 'static/fonts/DejaVuSans-Bold.ttf'))

    # создание и настройка макета
    c = canvas.Canvas(full_path, pagesize=landscape(A4))
    width, height = landscape(A4)
    margin = 10 * mm
    line_height = 7 * mm

    # отрисовка рамки
    c.setStrokeColor(colors.darkblue)
    c.setLineWidth(4)
    c.rect(margin, margin, width - 2 * margin, height - 2 * margin)

    # отрисовка логотипа
    if os.path.exists(logo_path):
        logo_w = 40 * mm
        logo_h = 40 * mm
        c.drawImage(logo_path, margin, height - margin - logo_h,
                    width=logo_w, height=logo_h, mask='auto')
    else:
        # отладочное сообщение
        c.setFont('DejaVuSans', 10)
        c.setFillColor(colors.red)
        c.drawString(margin + 5 * mm, height - margin - 5 * mm, "Logo not found")

    # функция для центрирования и разбиения текста на сроки (в случае необходимости)
    def draw_centered(text, y, font_size, font_name='DejaVuSans'):
        c.setFont(font_name, font_size)
        max_w = width - 2 * margin
        lines = simpleSplit(text, font_name, font_size, max_w)
        for i, line in enumerate(lines):
            yy = y - i * line_height
            c.drawCentredString(width / 2, yy, line)
        return y - (len(lines) - 1) * line_height

    # отрисовка названия оу, в котором выдан сертификат
    y = height - margin - 23 * mm
    y = draw_centered(univer_title, y, 18, 'DejaVuSans-Bold')

    # отрисовка надписей
    y -= line_height * 5
    c.setFillColor(colors.darkblue)
    y = draw_centered("Сертификат", y, 36, 'DejaVuSans-Bold')

    y -= line_height * 2
    c.setFillColor(colors.black)
    y = draw_centered("подтверждает, что", y, 18)

    # отрисовка ФИО студента, которому выдан сертификат
    y -= line_height * 1.5
    y = draw_centered(student_nsp, y, 24)

    # отрисовка нужно надписи в зависимости от типа достижения
    y -= line_height * 1.5
    if type != 'course':
        y = draw_centered(f"верифицировал(а) достижение «{course_title}»", y, 16)
    else:
        y = draw_centered(f"успешно прошёл(а) курс «{course_title}»", y, 16)

    # отрисовка оценки
    y -= line_height * 1.5
    y = draw_centered(f"С оценкой: {mark}", y, 16)

    # отрисовка нужно надписи в зависимости от типа достижения
    y -= line_height * 1.5
    if type != 'course':
        date_str = f"Достижение подтверждено: {end_date.strftime('%d.%m.%Y')}"
    else:
        date_str = f"Сроки обучения: {start_date.strftime('%d.%m.%Y')} — {end_date.strftime('%d.%m.%Y')}"
    y = draw_centered(date_str, y, 16)

    # отрисовка даты выдачи и кем выдан сертификат
    y -= line_height * 2
    y = draw_centered(f"Сертификат выдан: {univer_boss}, {datetime.now().strftime('%d.%m.%Y')}", y, 16)

    # отрисовка токена
    c.setFillColor(colors.grey)
    y = margin + 10 * mm
    draw_centered(f"Token: {token}", y, 10)

    # сохранение сертификата и возврат пути к файлу для сохранения в бд
    c.save()
    return short_path
