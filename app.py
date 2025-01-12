import os
from flask import Flask, render_template, request, redirect, url_for, session, flash
import mysql.connector
from werkzeug.utils import secure_filename
from dotenv import load_dotenv

# .env dosyasını yükle
load_dotenv()

app = Flask(__name__)

# Veritabanı bağlantısı
db = mysql.connector.connect(
    host=os.getenv("DATABASE_HOST"),
    user=os.getenv("DATABASE_USER"),  # Veritabanı kullanıcı adı
    password=os.getenv("DATABASE_PASSWORD"),  # Veritabanı şifresi
    database=os.getenv("DATABASE_NAME")  # Veritabanı adı
)

# Görsel Yükleme için Konfigürasyon
app.config['UPLOAD_FOLDER'] = os.getenv("UPLOAD_FOLDER")
app.config['ALLOWED_EXTENSIONS'] = set(os.getenv("ALLOWED_EXTENSIONS").split(","))

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/list')
def list_products():
    cursor = db.cursor(dictionary=True)
    cursor.execute(""" 
        SELECT urunler.urun_id, urunler.urun_ad, urunler.urun_fiyat, urunler.urun_stok, urunler.urun_resim, 
               urunler.urun_kategori 
        FROM urunler
    """)
    products = cursor.fetchall()
    return render_template('list_products.html', products=products)

@app.route('/add', methods=['GET', 'POST'])
def add_product():
    cursor = db.cursor(dictionary=True)
    if request.method == 'POST':
        urun_ad = request.form['urun_ad']
        urun_kategori = request.form['urun_kategori']
        urun_fiyat = request.form['urun_fiyat']
        urun_stok = request.form['urun_stok']
        urun_birim = request.form['urun_birim']

        # Resim Dosyasını Kontrol Et ve Kaydet
        filename = None
        if 'urun_resim' in request.files:
            file = request.files['urun_resim']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(file_path)

        # Ürünü Veritabanına Ekle
        cursor.execute("""
            INSERT INTO urunler (urun_ad, urun_kategori, urun_fiyat, urun_stok, urun_birim, urun_resim) 
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (urun_ad, urun_kategori, urun_fiyat, urun_stok, urun_birim, filename))
        db.commit()
        flash('Ürün başarıyla eklendi!', 'success')
        return redirect(url_for('list_products'))
    
    return render_template('add_product.html')

@app.route('/update/<int:product_id>', methods=['GET', 'POST'])
def update_product(product_id):
    cursor = db.cursor(dictionary=True)
    if request.method == 'POST':
        urun_ad = request.form['urun_ad']
        urun_kategori = request.form['urun_kategori']
        urun_fiyat = request.form['urun_fiyat']
        urun_stok = request.form['urun_stok']
        urun_birim = request.form['urun_birim']
        
        # Resim Dosyasını Kontrol Et ve Kaydet (Güncelleme işlemi)
        filename = None
        if 'urun_resim' in request.files:
            file = request.files['urun_resim']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(file_path)

        cursor.execute("""
            UPDATE urunler 
            SET urun_ad = %s, urun_kategori = %s, urun_fiyat = %s, urun_stok = %s, urun_birim = %s, urun_resim = %s 
            WHERE urun_id = %s
        """, (urun_ad, urun_kategori, urun_fiyat, urun_stok, urun_birim, filename, product_id))
        db.commit()
        flash('Ürün başarıyla güncellendi!', 'success')
        return redirect(url_for('list_products'))
    
    cursor.execute("SELECT * FROM urunler WHERE urun_id = %s", (product_id,))
    product = cursor.fetchone()
    return render_template('update_product.html', product=product)

@app.route('/delete/<int:product_id>', methods=['POST'])
def delete_product(product_id):
    cursor = db.cursor()
    cursor.execute("DELETE FROM urunler WHERE urun_id = %s", (product_id,))
    db.commit()
    flash('Ürün başarıyla silindi!', 'danger')
    return redirect(url_for('list_products'))

# Sepet sayfası
@app.route('/cart')
def cart():
    return render_template('cart.html')

# Sepete ürün ekleme
@app.route('/add_to_cart/<int:product_id>')
def add_to_cart(product_id):
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM urunler WHERE urun_id = %s", (product_id,))
    product = cursor.fetchone()

    # Sepet verisini saklamak için session kullanılabilir.
    if 'cart' not in session:
        session['cart'] = []
    session['cart'].append(product)
    session.modified = True

    flash('Ürün sepete eklendi!', 'success')
    return redirect(url_for('cart'))

# Sepetten ürün silme
@app.route('/remove_from_cart/<int:product_id>')
def remove_from_cart(product_id):
    if 'cart' in session:
        session['cart'] = [item for item in session['cart'] if item['urun_id'] != product_id]
        session.modified = True
        flash('Ürün sepetten silindi!', 'danger')
    return redirect(url_for('cart'))

if __name__ == '__main__':
    app.secret_key = os.getenv("SECRET_KEY")  # session için secret key çevresel değişkenden alınır
    app.run(debug=True)
