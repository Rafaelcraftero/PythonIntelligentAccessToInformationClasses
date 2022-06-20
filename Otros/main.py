import re
import urllib.error
from tkinter import *
from sqlite3 import *
import sqlite3
from tkinter import messagebox
from urllib import request
from bs4 import BeautifulSoup
import datetime
dbpath = "database.db"
sqlBadChars = [";", "'", "=", "\\", "\""]


def initDB():
   create_database()
   poblar_database()



def create_database():
   try:
       db_connection = connect(dbpath)
       db_connection.execute("DROP TABLE IF EXISTS EVENTOS")
       db_connection.execute("CREATE TABLE IF NOT EXISTS EVENTOS("
                             " ID INTEGER PRIMARY KEY AUTOINCREMENT,"
                             " TITULO TEXT NOT NULL,"
                             " LUGAR TEXT NOT NULL,"
                             " DIRECCION INTEGER,"
                             " POBLACION TEXT NOT NULL,"
                             " FECHA TEXT NOT NULL,"
                             " HORARIO TEXT NOT NULL,"
                             " CATEGORIAS TEXT NOT NULL)")
       db_connection.commit()
       db_connection.close()
   except Error as err:
       messagebox.showinfo("Error!", "Error creando la base de datos:\n" + str(err))
       return


def getAllElements():
   lista_elementos = []
   try:
       for i in range(1,5):
           film_webpage_url = "https://sevilla.cosasdecome.es/eventos/filtrar?pg=" + str(i)
           req = request.Request(film_webpage_url, headers={'User-Agent': 'Mozilla/5.0'})
           peticion = urllib.request.urlopen(req)
           pagina = peticion.read()
           peticion.close()
           soup = BeautifulSoup(pagina, 'html.parser')
           elementos = soup.find_all("article")
           for item in elementos:
               lista_elementos.append(item.find("a",href=True)['href'])
       return lista_elementos
   except urllib.error.URLError as urlError:
       messagebox.showinfo("Error", "Error descargando las webs:\n" + str(urlError))
       return None

def get_evento_data(evento_url):
   try:
           req = request.Request(evento_url, headers={'User-Agent': 'Mozilla/5.0'})
           peticion = urllib.request.urlopen(req)
           pagina = peticion.read()
           peticion.close()
           soup = BeautifulSoup(pagina, 'html.parser')
           titulo = soup.find("div","post-title").text
           lugar = "desconocido"
           buscalugar = soup.find("div","block-elto lugar")
           if buscalugar != None:
               lugar = buscalugar.find("div","value").text
           direccion = "desconocida"
           buscaDireccion = soup.find("div","block-elto direccion")
           if buscaDireccion != None:
               direccion = buscaDireccion.find("div","value").text
           horario = "desconocido"
           buscaHorario = soup.find("div","block-elto hora")
           if buscaHorario != None:
               horario = buscaHorario.text
           poblacion = soup.find("div","block-elto poblacion").find("div","block-listitem").text
           fecha = soup.find("div","post-date updated value").text
           categoria = soup.find("div","block-elto categoria").find("div","block-listitem").text
           return [titulo,lugar,direccion,poblacion,fecha, horario, categoria]
   except urllib.error.URLError as urlError:
       messagebox.showinfo("Error", "Error descargando las webs:\n" + str(urlError))
   return None




def poblar_database():
   lista_elementos =  getAllElements()
   try:
       db_connection = connect(dbpath)
       for elemento in lista_elementos:
           datos_eventos = get_evento_data(elemento)

           for caracter in sqlBadChars:
               datos_eventos[0] = datos_eventos[0].replace(caracter,"")
               datos_eventos[1] = datos_eventos[1].replace(caracter,"")
               datos_eventos[2] = datos_eventos[2].replace(caracter,"")
               datos_eventos[3] = datos_eventos[3].replace(caracter,"")
               datos_eventos[6] = datos_eventos[6].replace(caracter,"")

           db_connection.execute("INSERT INTO EVENTOS (TITULO,LUGAR,DIRECCION,POBLACION,FECHA,HORARIO,CATEGORIAS) VALUES ('"+datos_eventos[0]+"','"+datos_eventos[1]+"','"+datos_eventos[2]+"','"+datos_eventos[3]+"','"+datos_eventos[4]+"','"+datos_eventos[5]+"','"+datos_eventos[6]+"')")
       messagebox.showinfo("Info","Se ha creado la base de datos con un total de " + str(db_connection.total_changes) + " entradas")
       db_connection.commit()
       db_connection.close()
   except sqlite3.Error as err:
       messagebox.showinfo("Error", "Error poblando la base de datos:\n" + str(err))


def list_eventos(main_window):
   ventana_datos = Toplevel(main_window)
   ventana_datos.title("Todos los eventos")
   frameVentanaDatos = Frame(ventana_datos)
   frameVentanaDatos.pack(side=TOP, expand=1, fill=BOTH)
   listbox = Listbox(frameVentanaDatos)
   try:
       db_connection = connect(dbpath)
       eventos = db_connection.execute("SELECT TITULO,LUGAR,DIRECCION,POBLACION,FECHA,HORARIO,CATEGORIAS FROM EVENTOS").fetchall()
       for evento in eventos:

           listbox.insert(END,"------------------------------------------------")
           listbox.insert(END,"TITULO: " + evento[0])
           listbox.insert(END,"LUGAR: " + evento[1])
           listbox.insert(END,"DIRECCION: " + evento[2])
           listbox.insert(END,"POBLACION: " + evento[3])
           listbox.insert(END,"FECHA: " + evento[4])
           listbox.insert(END,"HORARIO: " + evento[5])
           listbox.insert(END,"CATEGORIAS: " + evento[6])
       db_connection.close()
   except sqlite3.Error as err:
       messagebox.showinfo("Error!", "Error listando películas:\n" + str(err))
       return
   listbox.pack(side=LEFT, expand=1, fill=BOTH)
   y_scrollbar = Scrollbar(frameVentanaDatos)
   y_scrollbar.pack(side=RIGHT, fill=Y)
   y_scrollbar.config(command=listbox.yview)
   listbox.config(yscrollcommand=y_scrollbar.set)

def list_eventos_por_la_noche(main_window):
   ventana_datos = Toplevel(main_window)
   ventana_datos.title("Eventos por la noche")
   frameVentanaDatos = Frame(ventana_datos)
   frameVentanaDatos.pack(side=TOP, expand=1, fill=BOTH)
   listbox = Listbox(frameVentanaDatos)
   try:
       db_connection = connect(dbpath)
       eventos = db_connection.execute("SELECT TITULO,LUGAR,DIRECCION,POBLACION,FECHA,HORARIO,CATEGORIAS FROM EVENTOS").fetchall()
       for evento in eventos:
           horario = evento[5].replace(" ","")
           buscaHora = re.match("\d{2}:\d{2}",horario)
           if buscaHora == None:
               if "cena" in horario.lower():
                   listbox.insert(END, "------------------------------------------------")
                   listbox.insert(END, "TITULO: " + evento[0])
                   listbox.insert(END, "LUGAR: " + evento[1])
                   listbox.insert(END, "DIRECCION: " + evento[2])
                   listbox.insert(END, "POBLACION: " + evento[3])
                   listbox.insert(END, "FECHA: " + evento[4])
                   listbox.insert(END, "HORARIO: " + evento[5])
                   listbox.insert(END, "CATEGORIAS: " + evento[6])
           else:
               parsedhora = datetime.datetime.strptime(horario,"%H:%M")
               parsedhoraLimite = datetime.datetime.strptime("19:00","%H:%M")
               if parsedhora >= parsedhoraLimite:
                   listbox.insert(END, "------------------------------------------------")
                   listbox.insert(END, "TITULO: " + evento[0])
                   listbox.insert(END, "LUGAR: " + evento[1])
                   listbox.insert(END, "DIRECCION: " + evento[2])
                   listbox.insert(END, "POBLACION: " + evento[3])
                   listbox.insert(END, "FECHA: " + evento[4])
                   listbox.insert(END, "HORARIO: " + evento[5])
                   listbox.insert(END, "CATEGORIAS: " + evento[6])

       db_connection.close()
   except sqlite3.Error as err:
       messagebox.showinfo("Error!", "Error listando películas:\n" + str(err))
       return
   listbox.pack(side=LEFT, expand=1, fill=BOTH)
   y_scrollbar = Scrollbar(frameVentanaDatos)
   y_scrollbar.pack(side=RIGHT, fill=Y)
   y_scrollbar.config(command=listbox.yview)
   listbox.config(yscrollcommand=y_scrollbar.set)

def fecha_input(main_window):
   ventana_input = Toplevel(main_window)
   ventana_input.title("Buscar por fecha")
   frame_ventana_input = Frame(ventana_input)
   frame_ventana_input.pack(side = TOP,expand=1,fill=BOTH)
   L1 = Label(frame_ventana_input, text="Introduzca la fecha (dia de mes de año): ")
   L1.pack(side=LEFT)
   titulo_entry = Entry(frame_ventana_input, bd=5)
   titulo_entry.pack(side=RIGHT)
   titulo_entry.bind("<Return>", lambda event : fecha_handler(titulo_entry.get(),ventana_input,main_window))

def fecha_handler(data,ventana_input,main_window):
   if re.match("\d{2} de .* de \d{4}",data) != None:
       fecha = datetime.datetime.strptime(data, "%d/%m/%Y")
       ventana_input.destroy()
       ventana_datos = Toplevel(main_window)
       ventana_datos.title("Búsqueda por fecha")
       frameVentanaDatos = Frame(ventana_datos)
       frameVentanaDatos.pack(side=TOP, expand=1, fill=BOTH)
       listbox = Listbox(frameVentanaDatos)
       try:
           db_connection = connect(dbpath)
           eventos = db_connection.execute("SELECT TITULO,LUGAR,DIRECCION,POBLACION,FECHA,HORARIO,CATEGORIAS FROM EVENTOS").fetchall()
           for evento in eventos:
               fecha_evento = evento[4]
                  # fecha_evento = datetime.datetime.strptime(evento[4].replace(" ",""), "%d/%m/%Y")
               if fecha == fecha_evento:
                   listbox.insert(END, "------------------------------------------------")
                   listbox.insert(END, "TITULO: " + evento[0])
                   listbox.insert(END, "LUGAR: " + evento[1])
                   listbox.insert(END, "DIRECCION: " + evento[2])
                   listbox.insert(END, "POBLACION: " + evento[3])
                   listbox.insert(END, "FECHA: " + evento[4])
                   listbox.insert(END, "HORARIO: " + evento[5])
                   listbox.insert(END, "CATEGORIAS: " + evento[6])

               db_connection.close()
       except sqlite3.Error as err:
           messagebox.showinfo("Error!", "Error listando películas:\n" + str(err))
           return
       listbox.pack(side=LEFT, expand=1, fill=BOTH)
       y_scrollbar = Scrollbar(frameVentanaDatos)
       y_scrollbar.pack(side=RIGHT, fill=Y)
       y_scrollbar.config(command=listbox.yview)
       listbox.config(yscrollcommand=y_scrollbar.set)
   else:
       messagebox.showinfo("Error","El formato de fecha introducido no es correcto")
       return

def input_buscar_categoria(main_window):
   ventana_datos = Toplevel(main_window)
   ventana_datos.title("Buscar por categoría")
   frameVentanaDatos = Frame(ventana_datos)
   frameVentanaDatos.pack(side=TOP, expand=1, fill=BOTH)
   try:
       db_conn = sqlite3.connect(dbpath)
   except:
       messagebox.showinfo("Error", "Se ha producido un error conectandose a la db")
       return
   try:
       generos_from_db = db_conn.execute("SELECT DISTINCT CATEGORIAS FROM EVENTOS")
   except sqlite3.Error as err:
       if re.match("no such table", str(err)):
           messagebox.showinfo("Error", "Todavía no has cargado los datos")
           return
       else:
           messagebox.showinfo("Error", "DB ERROR: " + str(err))
       return
   except:
       messagebox.showinfo("Error", "Error extrayendo datos de la bd")
       return
   fetched_db = generos_from_db.fetchall()
   db_conn.close()
   categorias = list(map(lambda x:x[0],fetched_db))
   label_categorias = Label(frameVentanaDatos,text="Seleccione la categoría")
   label_categorias.pack(side=LEFT, expand=1, fill=BOTH)
   spinbox_buscar_categoria = Spinbox(frameVentanaDatos, values=categorias, state= "readonly")
   spinbox_buscar_categoria.pack(side=LEFT, expand=1, fill=BOTH)
   spinbox_buscar_categoria.bind("<Return>", lambda event : buscar_genero_handler(spinbox_buscar_categoria.get(),ventana_datos,main_window))

def buscar_genero_handler(spinbox_buscar_categoria,last_window,main_window):
   valor_categoria = spinbox_buscar_categoria
   last_window.destroy()
   ventana_datos = Toplevel(main_window)
   ventana_datos.title("Búsqueda por categoría")
   frameVentanaDatos = Frame(ventana_datos)
   frameVentanaDatos.pack(side=TOP, expand=1, fill=BOTH)
   listbox = Listbox(frameVentanaDatos)
   try:
       db_connection = connect(dbpath)
       eventos = db_connection.execute(
           "SELECT TITULO,LUGAR,DIRECCION,POBLACION,FECHA,HORARIO,CATEGORIAS FROM EVENTOS WHERE CATEGORIAS = '"+valor_categoria+"' ORDER BY FECHA").fetchall()
       for evento in eventos:
           listbox.insert(END, "------------------------------------------------")
           listbox.insert(END, "TITULO: " + evento[0])
           listbox.insert(END, "LUGAR: " + evento[1])
           listbox.insert(END, "DIRECCION: " + evento[2])
           listbox.insert(END, "POBLACION: " + evento[3])
           listbox.insert(END, "FECHA: " + evento[4])
           listbox.insert(END, "HORARIO: " + evento[5])
           listbox.insert(END, "CATEGORIAS: " + evento[6])
       db_connection.close()
   except sqlite3.Error as err:
       messagebox.showinfo("Error!", "Error listando películas:\n" + str(err))
       return

   listbox.pack(side=LEFT, expand=1, fill=BOTH)
   y_scrollbar = Scrollbar(frameVentanaDatos)
   y_scrollbar.pack(side=RIGHT, fill=Y)
   y_scrollbar.config(command=listbox.yview)
   listbox.config(yscrollcommand=y_scrollbar.set)


def ventana_principal():
   root = Tk()
   root.geometry("150x100")
   menubar = Menu(root)
   datosmenu = Menu(menubar, tearoff=0)
   datosmenu.add_command(label="Cargar",command= initDB)
   datosmenu.add_separator()
   datosmenu.add_command(label="Salir", command=root.quit)
   menubar.add_cascade(label="Datos", menu=datosmenu)
   buscarmenu = Menu(menubar, tearoff=0)
   buscarmenu.add_command(label="Eventos", command= lambda :list_eventos(root))
   buscarmenu.add_command(label="Eventos por la noche", command= lambda : list_eventos_por_la_noche(root))
   menubar.add_cascade(label="Listar", menu=buscarmenu)
   buscarmenu = Menu(menubar, tearoff=0)
   buscarmenu.add_command(label="Fecha de celebración",command= lambda :fecha_input(root))
   buscarmenu.add_command(label="Eventos por categoría", command= lambda : input_buscar_categoria(root))
   menubar.add_cascade(label="Buscar", menu=buscarmenu)
   root.config(menu=menubar)
   root.mainloop()

ventana_principal()
