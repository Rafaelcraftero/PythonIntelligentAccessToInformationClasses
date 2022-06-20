# encoding:utf-8

from bs4 import BeautifulSoup
import urllib.request
from tkinter import *
from tkinter import messagebox
import sqlite3
import re
from datetime import datetime

PAGINAS = 4  # nÃºmero de pÃ¡ginas a cargar
PAGINA_INICIO = 1  # primera pÃ¡gina a cargar

# lineas para evitar error SSL
import os, ssl

if (not os.environ.get('PYTHONHTTPSVERIFY', '') and
        getattr(ssl, '_create_unverified_context', None)):
    ssl._create_default_https_context = ssl._create_unverified_context


def extraer_eventos():
    lista = []

    for p in range(PAGINA_INICIO, PAGINA_INICIO + PAGINAS):
        req = urllib.request.Request("https://sevilla.cosasdecome.es/eventos/filtrar?pg=" + str(p),
                                     headers={'User-Agent': 'Mozilla/5.0'})
        f = urllib.request.urlopen(req)
        s = BeautifulSoup(f, 'lxml')

        l = s.find_all('div', class_='post-details')

        for i in l:
            titulo = i.a.string.strip()

            req1 = urllib.request.Request(i.a['href'], headers={'User-Agent': 'Mozilla/5.0'})
            f1 = urllib.request.urlopen(req1)
            s1 = BeautifulSoup(f1, 'lxml')
            l1 = s1.find('section', class_='post-content')

            lugar = l1.find('div', class_='block-elto lugar')
            if lugar:
                lugar = lugar.find('div', class_='value').p.string.strip()
            else:
                lugar = "Desconocido"
            direccion = l1.find('div', class_='block-elto direccion')
            if direccion:
                direccion = direccion.find('div', class_='value').string.strip()
            else:
                direccion = "Desconocido"
            poblacion = l1.find('div', class_='block-elto poblacion')
            if poblacion:
                poblacion = poblacion.find('div', class_='value').a.string.strip()
            else:
                poblacion = "Desconocido"
            fechas = l1.find('div', class_='block-elto fechas')
            if fechas:
                fechas = fechas.i.next_sibling.strip()
                fechas = re.findall('\d{2}/\d{2}/\d{4}', fechas)
                fecha_inicio = datetime.strptime(fechas[0], '%d/%m/%Y')
                if (len(fechas) > 1):
                    fecha_fin = datetime.strptime(fechas[1], '%d/%m/%Y')
                else:
                    fecha_fin = fecha_inicio
            else:
                fecha_inicio = None
                fecha_fin = None
            hora = l1.find('div', class_='block-elto hora')
            if hora:
                hora = list(hora.find('div', class_='value').strings)[1].strip()
            else:
                hora = "Desconocido"
            categorias = l1.find('div', class_='block-elto categoria')
            if categorias:
                cat = categorias.find_all('div', class_='value')
                categorias = cat[0].a.string.strip()
                for i in range(1, len(cat)):
                    categorias = categorias + '/' + cat[i].a.string.strip()
            else:
                categorias = "Desconocido"

            lista.append((titulo, lugar, direccion, poblacion, fecha_inicio, fecha_fin, hora, categorias))

    return lista


def imprimir_lista(cursor):
    v = Toplevel()
    v.title("EVENTOS GASTRONÃ“MICOS EN SEVILLA")
    sc = Scrollbar(v)
    sc.pack(side=RIGHT, fill=Y)
    lb = Listbox(v, width=150, yscrollcommand=sc.set)
    for row in cursor:
        lb.insert(END, row[0])
        lb.insert(END, "    Lugar: " + row[1])
        lb.insert(END, "    DirecciÃ³n: " + row[2])
        lb.insert(END, "    PoblaciÃ³n: " + row[3])
        fecha_inicio = datetime.strptime(row[4], "%Y-%m-%d %H:%M:%S")
        fecha_fin = datetime.strptime(row[5], "%Y-%m-%d %H:%M:%S")
        fi = datetime.strftime(fecha_inicio, "%d/%m/%Y")
        ff = datetime.strftime(fecha_fin, "%d/%m/%Y")
        lb.insert(END, ("    Fechas: " + fi + " al " + ff) if fi != ff else ("    Fechas: " + fi))
        lb.insert(END, "    Horario: " + row[6])
        lb.insert(END, "    CategorÃ­as: " + row[7])
        lb.insert(END, "\n\n")
    lb.pack(side=LEFT, fill=BOTH)
    sc.config(command=lb.yview)


def cargar_bd():
    conn = sqlite3.connect('eventos.db')
    cursor = conn.execute("SELECT name FROM sqlite_master WHERE name='HORACARGA'")
    if (cursor.fetchone()):  # si ya existe una carga anterior
        c = conn.execute("SELECT * FROM HORACARGA")
        respuesta = messagebox.askyesno("Confirmar", "Base de datos ya existe.\nCargada el " + str(
            c.fetchone()[0]) + "\nDesea volver a cargar?")
        if respuesta:
            almacenar_bd()
    else:
        almacenar_bd()


def almacenar_bd():
    conn = sqlite3.connect('eventos.db')
    conn.text_factory = str  # para evitar problemas con el conjunto de caracteres que maneja la BD
    conn.execute("DROP TABLE IF EXISTS EVENTOS")
    conn.execute('''CREATE TABLE EVENTOS
       (TITULO        TEXT    NOT NULL,
       LUGAR          TEXT    ,
       DIRECCION         TEXT    ,
       POBLACION        TEXT    ,
       FECHA_INICIO        DATE    ,
       FECHA_FIN        DATE    ,
       HORA        TEXT    ,
       CATEGORIAS      TEXT);''')
    conn.execute("DROP TABLE IF EXISTS HORACARGA")
    conn.execute('''CREATE TABLE HORACARGA
       (HORA       DATE);''')
    # carga los eventos
    for i in extraer_eventos():
        conn.execute("""INSERT INTO EVENTOS VALUES (?,?,?,?,?,?,?,?)""", i)

    # guarda la hora de carga
    conn.execute("""INSERT INTO HORACARGA VALUES (?)""", (datetime.now(),))
    conn.commit()

    cursor = conn.execute("SELECT COUNT(*) FROM EVENTOS")
    messagebox.showinfo("Base Datos",
                        "Base de datos creada correctamente \nHay " + str(cursor.fetchone()[0]) + " registros")
    conn.close()


def listar_eventos():
    conn = sqlite3.connect('eventos.db')
    conn.text_factory = str
    cursor = conn.execute("SELECT * FROM EVENTOS")
    imprimir_lista(cursor)
    conn.close()


def listar_eventos_noche():
    conn = sqlite3.connect('eventos.db')
    conn.text_factory = str
    cursor = conn.execute("SELECT * FROM EVENTOS")
    lista = []
    for r in cursor:
        cena = re.search("cena", r[6])
        hora = re.search("(\d\d):\d\d", r[6])
        if cena:
            lista.append(r)
        else:
            if hora and int(hora.group(1)) >= 19:
                lista.append(r)
    imprimir_lista(lista)
    conn.close()


def buscar_por_fecha():
    def listar(event):
        conn = sqlite3.connect('eventos.db')
        conn.text_factory = str
        fec = re.match(r"(\d\d)\s+de\s+(\w+)\s+de\s+(\d{4})", str(entry.get().strip().lower()))
        if fec:
            meses = {"enero": "01", "febrero": "02", "marzo": "03", "abril": "04", "mayo": "05", "junio": "06",
                     "julio": "07",
                     "agosto": "08", "septiembre": "09", "octubre": "10", "noviembre": "11", "diciembre": "12"}
            fecha_aux = fec.group(1) + '/' + meses[fec.group(2)] + '/' + fec.group(3)
            fecha = datetime.strptime(fecha_aux, "%d/%m/%Y")
            cursor = conn.execute("SELECT * FROM EVENTOS WHERE FECHA_INICIO <= ? AND FECHA_FIN >= ?", (fecha, fecha))
            conn.close
            imprimir_lista(cursor)
        else:
            messagebox.showerror("Error", "Formato de fecha incorrecto")

    v = Toplevel()
    label = Label(v, text="Escriba la fecha (dd de Mes de aaaa): ")
    label.pack(side=LEFT)
    entry = Entry(v)
    entry.bind("<Return>", listar)
    entry.pack(side=LEFT)


def buscar_por_categoria():
    def listar(event):
        conn = sqlite3.connect('eventos.db')
        conn.text_factory = str
        cursor = conn.execute("SELECT * FROM EVENTOS WHERE CATEGORIAS LIKE '%" + str(categoria.get()) + "%'")
        conn.close
        imprimir_lista(cursor)

    conn = sqlite3.connect('eventos.db')
    conn.text_factory = str
    cursor = conn.execute("SELECT DISTINCT CATEGORIAS FROM EVENTOS")

    categorias = set()
    for i in cursor:
        varios = i[0].split("/")
        for t in varios:
            categorias.add(t.strip())

    v = Toplevel()
    label = Label(v, text="Seleccione la categorÃ­a: ")
    label.pack(side=LEFT)
    categoria = Spinbox(v, width=30, values=list(categorias))
    categoria.bind("<Return>", listar)
    categoria.pack(side=LEFT)

    conn.close()


def ventana_principal():
    root = Tk()
    root.geometry("150x100")

    menubar = Menu(root)

    datosmenu = Menu(menubar, tearoff=0)
    datosmenu.add_command(label="Cargar", command=cargar_bd)
    datosmenu.add_separator()
    datosmenu.add_command(label="Salir", command=root.quit)

    menubar.add_cascade(label="Datos", menu=datosmenu)

    buscarmenu = Menu(menubar, tearoff=0)
    buscarmenu.add_command(label="Eventos", command=listar_eventos)
    buscarmenu.add_command(label="Eventos por la noche", command=listar_eventos_noche)

    menubar.add_cascade(label="Listar", menu=buscarmenu)

    buscarmenu = Menu(menubar, tearoff=0)
    buscarmenu.add_command(label="Buscar por fecha", command=buscar_por_fecha)
    buscarmenu.add_command(label="Eventos por categorÃ­a", command=buscar_por_categoria)

    menubar.add_cascade(label="Buscar", menu=buscarmenu)

    root.config(menu=menubar)
    root.mainloop()


if __name__ == "__main__":
    ventana_principal()