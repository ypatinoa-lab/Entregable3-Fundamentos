import os
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

app = Flask(__name__)

# Configuración de la base de datos online (o local por defecto)
# Nota: Si la URL de Postgres empieza por postgres://, SQLAlchemy requiere que sea postgresql://
db_url = os.getenv('DATABASE_URL', 'sqlite:///inventario.db')
if db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql://", 1)

app.config['SQLALCHEMY_DATABASE_URI'] = db_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Modelo de la base de datos
class Producto(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    cantidad = db.Column(db.Integer, nullable=False)
    precio = db.Column(db.Float, nullable=False)
    fecha_compra = db.Column(db.Date, nullable=False)
    fecha_venta = db.Column(db.Date, nullable=True)

# Crear tablas si no existen
with app.app_context():
    db.create_all()

@app.route('/')
def index():
    productos = Producto.query.all()
    inventario = []
    
    # Lógica de negocio (Cálculo de IVA y Estado de agotado)
    for p in productos:
        iva = p.precio * 0.19  # IVA del 19% (Colombia)
        precio_total = p.precio + iva
        agotado = p.cantidad <= 0
        
        inventario.append({
            'id': p.id,
            'nombre': p.nombre,
            'cantidad': p.cantidad,
            'precio': p.precio,
            'iva': iva,
            'precio_total': precio_total,
            'fecha_compra': p.fecha_compra.strftime('%Y-%m-%d'),
            'fecha_venta': p.fecha_venta.strftime('%Y-%m-%d') if p.fecha_venta else 'N/A',
            'agotado': agotado
        })
        
    return render_template('index.html', productos=inventario)

@app.route('/agregar', methods=['POST'])
def agregar():
    if request.method == 'POST':
        nombre = request.form['nombre']
        cantidad = int(request.form['cantidad'])
        precio = float(request.form['precio'])
        fecha_compra = datetime.strptime(request.form['fecha_compra'], '%Y-%m-%d').date()
        
        fecha_venta_str = request.form['fecha_venta']
        fecha_venta = datetime.strptime(fecha_venta_str, '%Y-%m-%d').date() if fecha_venta_str else None

        nuevo_producto = Producto(
            nombre=nombre,
            cantidad=cantidad,
            precio=precio,
            fecha_compra=fecha_compra,
            fecha_venta=fecha_venta
        )
        
        db.session.add(nuevo_producto)
        db.session.commit()
        return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)