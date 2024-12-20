import mysql.connector,funciones,os
from flask import Flask, render_template,flash, request,  redirect, url_for
from datetime import datetime
from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__)
app.secret_key=os.getenv("APP_KEY")
DB_HOST =os.getenv('DB_HOST')
DB_USERNAME =os.getenv("DB_USERNAME")
DB_PASSWORD =os.getenv("DB_PASSWORD")
DB_NAME =os.getenv("DB_NAME")

# Connect to the database
connection =mysql.connector.connect(
    host=DB_HOST,
    user=DB_USERNAME,
    password=DB_PASSWORD,
    database=DB_NAME,
    autocommit=True
)

@app.route("/")
def login():   
    cur = connection.cursor() 
    resultado=funciones.listado_paradas(cur)
    paradas=[]
    for paradax in resultado:
       paradas+=paradax  
    cur.close()                   
    return render_template('login.html',paradas=paradas)

@app.route("/verificador", methods=["GUET","POST"])
def verificador(): 
   msg = ''
   global parada 
   if request.method == 'POST':        
    parada = request.form['parada']
    cedula = request.form['cedula']
    password = request.form['clave']   
    cur = connection.cursor()    
    estacion=funciones.check_parada(cur,parada)
    if estacion == True:           
        cur.execute(f"SELECT cedula FROM {parada} WHERE cedula='{cedula}'")
        result = cur.fetchall()
        if result != []:   
         cur.execute(f"SELECT password FROM tabla_index  WHERE nombre ='{parada}'" )
         ident=cur.fetchall() 
         for idx in ident:  
            if password == idx[0]:                                                                          
                fecha = datetime.strftime(datetime.now(),"%Y %m %d - %H")
                informacion=funciones.info_parada(cur,parada) 
                cabecera=funciones.info_cabecera(cur,parada) 
                miembros=funciones.lista_miembros(cur,parada)                
                diario=funciones.diario_general(cur,parada) 
                cuotas_hist=funciones.prestamo_aport(cur,parada)
                cur.close()
                return render_template('index.html',informacion=informacion,cabecera=cabecera,fecha=fecha,miembros=miembros,diario=diario,cuotas_hist=cuotas_hist)                 
            else:
               msg = 'Incorrecta contraseña de la parada!'          
               flash(msg)           
               return redirect(url_for('login'))    
        else:    
          msg = 'cedula Incorrecta para esta parada!'
          flash(msg)           
          return redirect(url_for('login'))    
    else:
      msg = 'Esta parada esta inoperante!' 
      flash(msg)          
      return redirect(url_for('login'))            



if __name__ == "__main__":
    app.run(debug=True,host='0.0.0.0')
