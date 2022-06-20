
# Práctica realizada por José Guisado Simón, Jaime Lopez Marquez, Rafael Balbuena Lopez
import datetime
import gettext
import os.path
from bs4 import BeautifulSoup
from tkinter import *
from tkinter import messagebox
import urllib
import re
from whoosh.fields import Schema, TEXT, ID, KEYWORD, DATETIME
from whoosh.index import create_in, open_dir
from whoosh.qparser import MultifieldParser, QueryParser
from whoosh import qparser
import os
import ssl
from urllib import request

num_paginas = 2
page_url = "https://www.sensacine.com/noticias/"
meses = { "enero" : "01", "febrero": "02","marzo":"03","abril":"04","mayo":"05","junio":"06","julio":"07","agosto":"08",
       "septiembre":"09","octubre":"10","noviembre":"11","diciembre":"12" }

def ask_y_n():
   if os.path.exists("index"):
       res = messagebox.askyesno("Info","Los datos parecen estar ya cargados, quiere volver a cargarlos?")
       if res:
           carga_datos()
   else:
       carga_datos()

def carga_datos():
   crea_index()
   ix = open_dir("index")
   writer = ix.writer()
   for film_data in get_all_films():
       splittedFecha = film_data[4].split(",")[1]
       splittedFecha_spaces = splittedFecha.strip().split()
       if int(splittedFecha_spaces[0])>=10:
           fecha = splittedFecha_spaces[0] + "/" + meses[splittedFecha_spaces[2]] + "/" + splittedFecha_spaces[4]
       else:
           fecha = "0" +splittedFecha_spaces[0] + "/" + meses[splittedFecha_spaces[2]] + "/" + splittedFecha_spaces[4]

       fecha_datetime = datetime.datetime.strptime(fecha,"%d/%m/%Y")
       writer.add_document(titulo=film_data[0],
                           categoria=film_data[1],
                           enlace=film_data[2],
                           descripcion=film_data[3],
                           fecha=fecha_datetime)
   writer.commit()
   messagebox.showinfo("Info", "Se han cargado un total de " + str(ix.reader().doc_count()) + " peliculas")

def crea_index():
   schema = Schema(titulo=TEXT(stored=True),
                   categoria=KEYWORD(stored=True, commas=True),
                   enlace=ID(stored=True,unique=True),
                   descripcion=TEXT(stored=True),
                   fecha=DATETIME(stored=True))
   if not os.path.exists("index"):
       os.mkdir("index")
   create_in("index", schema)


def get_all_films():
   film_data = []
   for i in range(1, num_paginas+1):
       try:
           req = urllib.request.Request(page_url + "?page=" + str(i),
                                        headers={'User-Agent': 'Mozilla/5.0'})
           f = urllib.request.urlopen(req)
           s = BeautifulSoup(f, 'html.parser')
           noticias = s.find("div","gd-col-left").find_all("div","card")
           for noticia in noticias:
               titulo = "desconocido"
               categoria = "desconocida"
               enlace = "desconocido"
               descripcion = "desconocido"
               fecha = "desconocida"
               find_titulo= noticia.find("h2","meta-title")
               find_categoria = noticia.find("div","meta-category")
               find_enlace = noticia.find("a","meta-title-link")
               find_descripcion = noticia.find("div","meta-body")
               find_fecha = noticia.findNext ("div","meta-date")
               if find_titulo != None:
                   titulo = find_titulo.text
               if find_categoria != None:
                   categoria = find_categoria.text
               if find_enlace != None:
                   enlace = "https://www.sensacine.com" + find_enlace['href']
               if  find_descripcion != None:
                   descripcion = find_descripcion.text
               if find_fecha != None:
                   fecha = find_fecha.text
               film_data.append([titulo,categoria,enlace,descripcion,fecha])
       except:
           messagebox.showerror("Error", "Error indexing games a page: " + page_url + str(i))
   return film_data

def descripcion_input():
   ventana_input = Toplevel(root)
   ventana_input.title("Busqueda en descripcion")
   frame_ventana_input = Frame(ventana_input)
   frame_ventana_input.pack(side = TOP,expand=1,fill=BOTH)
   L1 = Label(frame_ventana_input, text="Introduzca la frase a buscar:")
   L1.pack(side=LEFT)
   titulo_entry = Entry(frame_ventana_input, bd=5)
   titulo_entry.pack(side=RIGHT)
   titulo_entry.bind("<Return>", lambda event : descripcion_handler(titulo_entry.get(),ventana_input))


def descripcion_handler(data,ventana_input):
   ventana_input.destroy()
   ix = open_dir("index")
   query = QueryParser('descripcion',ix.schema).parse(str(data))
   resultado = ix.searcher().search(query)
   print_result_listbox(resultado,["titulo","categoria","enlace","fecha"])

def print_result_listbox(resultado, params):
   if len(resultado) == 0:
       messagebox.showinfo("Info", "No hay ningún resultado con esa consulta")
   else:
       ventana_datos = Toplevel(root)
       ventana_datos.title("Resultado búsqueda")
       frameVentanaDatos = Frame(ventana_datos)
       frameVentanaDatos.pack(side=TOP, expand=1, fill=BOTH)
       listbox = Listbox(frameVentanaDatos)
       for documento in resultado:
           listbox.insert(END, "------------------------------------------------")
           for param in params:
               if param == "fecha":
                   listbox.insert(END, param +" : "+ datetime.datetime.strftime(documento[param],"%d/%m/%Y"))
               else:
                   listbox.insert(END, param +" : "+ documento[param])
       listbox.pack(side=LEFT, expand=1, fill=BOTH)
       y_scrollbar = Scrollbar(frameVentanaDatos)
       y_scrollbar.pack(side=RIGHT, fill=Y)
       y_scrollbar.config(command=listbox.yview)
       listbox.config(yscrollcommand=y_scrollbar.set)

def fecha_input():
   ventana_input = Toplevel(root)
   ventana_input.title("Busqueda por fecha")
   frame_ventana_input = Frame(ventana_input)
   frame_ventana_input.pack(side = TOP,expand=1,fill=BOTH)
   frame_ventana_input2 = Frame(ventana_input)
   frame_ventana_input2.pack(side = BOTTOM,expand=1,fill=BOTH)
   L1 = Label(frame_ventana_input, text="Introduzca la fecha de inicio:")
   L1.pack(side=LEFT)
   fechaInicioEntry = Entry(frame_ventana_input, bd=5)
   fechaInicioEntry.pack(side=RIGHT)
   L2 = Label(frame_ventana_input2, text="Introduzca la fecha de destino:")
   L2.pack(side=LEFT)
   fechaDestinoEntry = Entry(frame_ventana_input2, bd=5)
   fechaDestinoEntry.pack(side=RIGHT)

   fechaInicioEntry.bind("<Return>", lambda event : fecha_handler(fechaInicioEntry.get(),fechaDestinoEntry.get(),ventana_input))
   fechaDestinoEntry.bind("<Return>", lambda event : fecha_handler(fechaInicioEntry.get(),fechaDestinoEntry.get(),ventana_input))

def fecha_handler(fecha_inicio,fecha_destino,ventana):
   try:
       fecha1= datetime.datetime.strptime(fecha_inicio,"%d/%m/%Y")
       fecha2= datetime.datetime.strptime(fecha_destino,"%d/%m/%Y")
   except:
       messagebox.showerror("Error","El formato de las fechas no es el correcto DD/MM/YYYY")
       return
   ix = open_dir("index")
   q = QueryParser("fecha", schema=ix.schema).parse(u"fecha_estreno:["+fecha1.strftime("%Y%m%d") + " TO " + fecha2.strftime("%Y%m%d")+"]")
   resultado = ix.searcher().search(q,limit=200)
   print_result_listbox(resultado, ["titulo","categoria", "enlace"])

def imprimir_lista(cursor):
    v = Toplevel()
    v.title("Noticias de sensacine")
    sc = Scrollbar(v)
    sc.pack(side=RIGHT, fill=Y)
    lb = Listbox(v, width=150, yscrollcommand=sc.set)
    for row in cursor:
        lb.insert(END, row['titulo'])
        lb.insert(END, "    Categoria: " + row['categoria'])
        lb.insert(END, "    Descripcion: " + row['descripcion'])
        lb.insert(END, "\n\n")
    lb.pack(side=LEFT, fill=BOTH)
    sc.config(command=lb.yview)

def buscar_categoriasytitulos():
    def mostrar_lista():
        ix = open_dir("Index")

        with ix.searcher() as searcher:
            entradaCategoria = Spb.get().lower()
            entradaTitulo = en.get().lower()
            # se busca como una frase porque hay categorias con varias palabras
            query = QueryParser("categoria", ix.schema).parse('"' + entradaCategoria + '"')
            query = "SELECT * IN "
            query=query + "WHERE `titulo`.contains('{$entradaTitulo}')"
            entradaTitulo = searcher.search(query)
            imprimir_lista(entradaTitulo)

    v = Toplevel()
    v.title("Categoria y titulo")
    l = Label(v, text="Categoria y titulo:")
    l.pack(side=LEFT)

    ix = open_dir("Index")
    with ix.searcher() as searcher:
        # lista de todas las categorias disponibles en el campo de categorias
        lista_categoriasytitulos = [i.decode('utf-8') for i in searcher.lexicon('categoria')]
    arrayString={}
    Spb = Spinbox(v, values=lista_categoriasytitulos, state="readonly")
    Spb.pack(side=LEFT)
    en = Entry(v, width=75)
    en.pack(side=LEFT)

    bt = Button(v, text='Buscar', command=mostrar_lista)
    bt.pack(side=LEFT)


root = Tk()
root.geometry("150x100")
menubar = Menu(root)
datosmenu = Menu(menubar, tearoff=0)
datosmenu.add_command(label="Cargar", command=ask_y_n)
datosmenu.add_separator()
datosmenu.add_command(label="Salir", command=root.quit)
menubar.add_cascade(label="Buscar", menu=datosmenu)
buscarmenu = Menu(menubar, tearoff=0)
buscarmenu.add_command(label="Descripcion",command=descripcion_input)
buscarmenu.add_separator()
buscarmenu.add_command(label="Categoria y Titulo",command=buscar_categoriasytitulos)
buscarmenu.add_separator()
buscarmenu.add_command(label="Fecha", command=fecha_input)
buscarmenu.add_separator()
buscarmenu.add_command(label="Fecha")
buscarmenu.add_separator()
buscarmenu.add_command(label="Modificar fecha")
menubar.add_cascade(label="Buscar", menu=buscarmenu)
buscarmenu = Menu(menubar, tearoff=0)
root.config(menu=menubar)
root.mainloop()




