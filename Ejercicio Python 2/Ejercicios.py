# encoding:utf-8

import urllib.request
from tkinter import *
from tkinter import messagebox
import sqlite3
import dateutil.parser


def abrir_url(url, file):
    try:
        urllib.request.urlretrieve(url, file)
        return file
    except:
        print("Error al conectarse a la página")
        return None


def extraer_datos():
    fichero = "noticias"
    if abrir_url("https://sevilla.abc.es/rss/feeds/Sevilla_Sevilla.xml", fichero):
        f = open(fichero, "r", encoding='utf-8')
        s = f.read()
        l1 = re.findall(r'<item>\s*<title>(.*)</title>\s*<link>(.*)</link>', s)
        l2 = re.findall(r'<pubDate>(.*)</pubDate>', s)
        l = []
        l = [list(e1) for e1 in l1]
        for e1, e2 in zip(l, l2):
            e1.append(e2)
        f.close()
        return l[1:]


def almacenar_bd():
    conn = sqlite3.connect('noticias.db')
    conn.text_factory = str  # para evitar problemas con el conjunto de caracteres que maneja la BD
    conn.execute("DROP TABLE IF EXISTS NOTICIAS")
    conn.execute('''CREATE TABLE NOTICIAS
       (ID INTEGER PRIMARY KEY  AUTOINCREMENT,
       TITULO           TEXT    NOT NULL,
       LINK           TEXT    NOT NULL,
       FECHA        DATE NOT NULL);''')
    l = extraer_datos()
    for i in l:
        conn.execute("""INSERT INTO NOTICIAS (TITULO, LINK, FECHA) VALUES (?,?,?)""", (i[0], i[1], i[2]))
    conn.commit()
    cursor = conn.execute("SELECT COUNT(*) FROM NOTICIAS")
    messagebox.showinfo("Base Datos",
                        "Base de datos creada correctamente \nHay " + str(cursor.fetchone()[0]) + " registros")
    conn.close()


def listar_bd():
    conn = sqlite3.connect('noticias.db')
    conn.text_factory = str
    cursor = conn.execute("SELECT TITULO,LINK, FECHA FROM NOTICIAS")
    imprimir_etiqueta(cursor)
    conn.close()


def imprimir_etiqueta(cursor):
    v = Toplevel()
    sc = Scrollbar(v)
    sc.pack(side=RIGHT, fill=Y)
    lb = Listbox(v, width=150, yscrollcommand=sc.set)
    for row in cursor:
        lb.insert(END, row[0])
        lb.insert(END, row[1])
        lb.insert(END, row[2])
        lb.insert(END, '')
    lb.pack(side=LEFT, fill=BOTH)
    sc.config(command=lb.yview)


def imprimir_etiqueta_1(cursor, fecha):
    v = Toplevel()
    sc = Scrollbar(v)
    sc.pack(side=RIGHT, fill=Y)
    lb = Listbox(v, width=150, yscrollcommand=sc.set)
    for row in cursor:
        if dateutil.parser.parse(fecha, dayfirst=True).date() == dateutil.parser.parse(row[2]).date():
            lb.insert(END, row[0])
            lb.insert(END, row[1])
            lb.insert(END, row[2])
            lb.insert(END, '')
    lb.pack(side=LEFT, fill=BOTH)
    sc.config(command=lb.yview)


def buscar_mes_bd():
    def listar_busqueda(event):
        conn = sqlite3.connect('noticias.db')
        conn.text_factory = str
        s = "%" + en.get() + "%"
        cursor = conn.execute("""SELECT TITULO,LINK,FECHA FROM NOTICIAS WHERE FECHA LIKE ?""",
                              (s,))  # al ser de tipo string, el ? le pone comillas simples
        imprimir_etiqueta(cursor)
        conn.close()

    v = Toplevel()
    lb = Label(v, text="Introduzca el mes (Xxx): ")
    lb.pack(side=LEFT)
    en = Entry(v)
    en.bind("<Return>", listar_busqueda)
    en.pack(side=LEFT)


def buscar_dia_bd():
    def listar_busqueda(event):
        conn = sqlite3.connect('noticias.db')
        conn.text_factory = str
        cursor = conn.execute("""SELECT TITULO,LINK,FECHA FROM NOTICIAS""")
        imprimir_etiqueta_1(cursor, en.get())
        conn.close()

    v = Toplevel()
    lb = Label(v, text="Introduzca la fecha (dd/mm/aaaa): ")
    lb.pack(side=LEFT)
    en = Entry(v)
    en.bind("<Return>", listar_busqueda)
    en.pack(side=LEFT)


def ventana_principal():
    top = Tk()
    almacenar = Button(top, text="Almacenar", command=almacenar_bd)
    almacenar.pack(side=LEFT)
    listar = Button(top, text="Listar", command=listar_bd)
    listar.pack(side=LEFT)
    Buscar = Button(top, text="Busca Mes", command=buscar_mes_bd)
    Buscar.pack(side=LEFT)
    Buscar = Button(top, text="Busca Día", command=buscar_dia_bd)
    Buscar.pack(side=LEFT)
    top.mainloop()


if __name__ == "__main__":
    ventana_principal()
