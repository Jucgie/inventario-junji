#se importa flask
from flask import Blueprint, render_template, request, url_for, redirect,flash, session
#se importa dependencias para conexion con mysql
from db import mysql
#importamos el modulo que creamos
from funciones import validarChar, getPerPage
from cuentas import loguear_requerido, administrador_requerido
from cerberus import Validator
proveedor = Blueprint('proveedor', __name__, template_folder='app/templates')

# Definir el esquema de validación para el proveedor
schema_proveedor = {
    'nombre_proveedor': {
        'type': 'string',
        'minlength': 1,
        'maxlength': 100,
        'regex': '^[a-zA-Z0-9]*$'  # Permitir solo letras, números y espacios
    }
}

#se especifica la ruta principal para la vista de proveedor 
@proveedor.route('/proveedor')
@proveedor.route('/proveedor/<page>')
@loguear_requerido
def Proveedor(page = 1):
    if "user" not in session:
        flash("you are NOT authorized")
        return redirect("/ingresar")
    page = int(page)
    perpage = getPerPage()
    offset  = (page -1) * perpage
    #el cursor permite interactuar con la base de datos
    cur = mysql.connection.cursor()
    cur.execute('SELECT * FROM proveedor LIMIT %s OFFSET %s',(perpage, offset))
    #almacenamos los datos consultados en una variable
    data = cur.fetchall()
    #se retorna la vista con render_template y la informacion de la base de datos de los proveedores para ser manipulados
    cur.execute('SELECT COUNT(*) FROM proveedor')
    total = cur.fetchone()
    total = int(str(total).split(':')[1].split('}')[0])
    return render_template('proveedor.html', proveedor = data, 
                           page = page, lastpage = page < (total/perpage)+1)

#se especifica la ruta para agregar proveedores, como tambien el metodo por el cual extrae los datos desde el formulario
@proveedor.route('/add_proveedor', methods = ['POST'])  
#se define una funcion  
@administrador_requerido
def add_proveedor():       
    if "user" not in session:
        flash("you are NOT authorized")
        return redirect("/ingresar")
    if request.method == 'POST':
       # Obtener el dato del formulario
        data = {
            'nombre_proveedor': request.form['nombre_proveedor']
        }

        # Validar los datos usando Cerberus
        v = Validator(schema_proveedor)
        if not v.validate(data):
            flash("Caracteres no permitidos")
            return redirect(url_for('proveedor.Proveedor'))

        #generaremos un try catch para que no se caiga la app
        try:
                #el cursor() permite generar consultas sql          
                cur = mysql.connection.cursor()
                #se especifica la consulta sql
                cur.execute('INSERT INTO proveedor (nombreProveedor) VALUES(%s)', (data["nombre_proveedor"],))
                #esta linea se utiliza para realizar la consulta sql
                mysql.connection.commit()
                flash('Proveedor agregado exitosamente')
                #se retorna a la vista de proveedor
                return redirect(url_for('proveedor.Proveedor'))  
        #dara una excepcion si es que falla la consulta u otro tipo de error             
        except Exception as e:
            #flash retornara el error 
            #flash(e.args[1])
            flash("Error al crear")
            #generado el error redirije a la pagina principal
            return redirect(url_for('proveedor.Proveedor'))

#ruta para enviar datos a la vista de editarProveedor con el id correspondiente
@proveedor.route('/edit_proveedor/<id>', methods = ['POST', 'GET'])
#en esta funcion se agrega el id como parametro
@administrador_requerido
def edit_proveedor(id):
    if "user" not in session:
        flash("you are NOT authorized")
        return redirect("/ingresar")
    try:
        cur = mysql.connection.cursor()
        #%s sirve como marcador de posicion para las variables que mencionaremos a prosteriori, 
        #como esta pensada para varios datos, estos deben ser mencionados dentro de una tupla, si es un solo dato mencionamos el dato y agregamos una coma ,
        cur.execute('SELECT * FROM proveedor WHERE idProveedor = %s', (id,))
        data = cur.fetchall()
        #como llamaremos seleccionamos los datos del proveedor dependiendo el valor de data[0] (el id que seleccionamos)
        return render_template('editProveedor.html' , proveedor = data[0])
    except Exception as e:
            #flash(e.args[1])
            flash("Error al crear")
            return redirect(url_for('proveedor.Proveedor'))

#ruta para poder actualizar los datos de proveedor dependiendo del id
@proveedor.route('/update_proveedor/<id>', methods = ['POST'])
@administrador_requerido
def actualizar_proveedor(id):
    if request.method == 'POST':
         # Obtener el dato del formulario
        data = {
            'nombre_proveedor': request.form['nombre_proveedor']
        }

        # Validar los datos usando Cerberus
        v = Validator(schema_proveedor)
        if not v.validate(data):
            flash("Caracteres no permitidos")
            return redirect(url_for('proveedor.Proveedor'))
        
        try:
            cur = mysql.connection.cursor()
            cur.execute(""" 
            UPDATE proveedor 
            SET nombreProveedor = %s
            WHERE idProveedor = %s                                    
            """, (data["nombre_proveedor"], id))
            mysql.connection.commit()
            flash('Proveedor actualizado correctamente')
            return redirect(url_for('proveedor.Proveedor'))
        except Exception as e:
            #flash(e.args[1])
            flash("Error al crear")
            return redirect(url_for('proveedor.Proveedor'))
    
#ruta para poder eliminar un proveedor por id
@proveedor.route('/delete_proveedor/<id>', methods = ['POST', 'GET'])
@administrador_requerido
def delete_proveedor(id):
    if "user" not in session:
        flash("you are NOT authorized")
        return redirect("/ingresar")
    try:
        cur = mysql.connection.cursor()
        cur.execute('DELETE FROM proveedor WHERE idProveedor = %s', (id,))
        mysql.connection.commit()
        flash('Proveedor eliminado correctamente')
        return redirect(url_for('proveedor.Proveedor'))
    except Exception as e:
        #flash(e.args[1])
        flash("Error al crear")
        return redirect(url_for('proveedor.Proveedor'))

