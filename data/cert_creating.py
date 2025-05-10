import uuid
import os
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
from reportlab.lib.colors import grey
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
import hashlib


def tokenize():
    return str(uuid.uuid4())


def hash_name(st, co, un_t):
    raw = f"{st}_{co}_{un_t}"
    hash_obj = hashlib.sha256(raw.encode('utf-8'))
    return hash_obj.hexdigest()


def pdf_creating(student_nsp, course_title, univer_title, start_date, end_date, univer_boss, token, mark="—"):
    os.makedirs('static/achievements', exist_ok=True)

    clean_student = student_nsp.replace(' ', '_')
    clean_course = course_title.replace(' ', '_')
    filename_only = f"cert_{hash_name(clean_student, clean_course, univer_title)}.pdf"
    full_path = os.path.join('static/achievements', filename_only)
    short_path = os.path.join('achievements', filename_only)

    pdfmetrics.registerFont(TTFont('DejaVuSans', 'static/fonts/DejaVuSans.ttf'))
    pdfmetrics.registerFont(TTFont('DejaVuSans-Bold', 'static/fonts/DejaVuSans-Bold.ttf'))

    c = canvas.Canvas(full_path, pagesize=A4)
    width, height = A4

    c.setFont("DejaVuSans-Bold", 16)
    c.drawCentredString(width / 2, height - 3 * cm, univer_title)

    c.setFont("DejaVuSans", 14)
    c.drawCentredString(width / 2, height / 2 + 2.5 * cm,
                        f"{student_nsp} успешно завершил(а) курс")
    c.drawCentredString(width / 2, height / 2 + 1.8 * cm, f"«{course_title}»")

    c.setFont("DejaVuSans-Bold", 14)
    c.drawCentredString(width / 2, height / 2 + 1.0 * cm, f"с оценкой: {mark}")

    c.setFont("DejaVuSans", 12)
    c.drawRightString(width - 2.5 * cm, height / 2 + 0.15 * cm,
                      f"Сроки обучения: {start_date.strftime('%d.%m.%Y')} — {end_date.strftime('%d.%m.%Y')}")
    c.drawString(2.5 * cm, 6 * cm, f"Сертификат выдан: {univer_boss}")


    c.setFont("DejaVuSans", 8)
    c.setFillColor(grey)
    c.drawCentredString(width / 2, 1.5 * cm, f"token: {token}")
    c.setFillColor("black")

    c.save()
    return short_path