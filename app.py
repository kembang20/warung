import sqlite3
from flask import Flask, render_template, jsonify, request
from datetime import datetime

app = Flask(__name__)

def get_db_connection():
    conn = sqlite3.connect('warung.db', check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

# Inisialisasi Database
def init_db():
    conn = get_db_connection()
    # Tabel stok
    conn.execute('''CREATE TABLE IF NOT EXISTS inventory 
                    (id INTEGER PRIMARY KEY, kategori TEXT, nama TEXT, stok INTEGER, harga INTEGER)''')
    # Tabel transaksi (untuk mencatat penjualan per hari)
    conn.execute('''CREATE TABLE IF NOT EXISTS transaksi 
                    (id INTEGER PRIMARY KEY, nama_barang TEXT, tanggal TEXT, jumlah_jual INTEGER)''')
    conn.commit()
    conn.close()

init_db()

@app.route('/api/tambah-barang', methods=['POST'])
def tambah_barang():
    data = request.json
    conn = get_db_connection()
    conn.execute('INSERT INTO inventory (kategori, nama, stok, harga) VALUES (?, ?, ?, ?)', 
                 (data['kategori'], data['nama'], data['stok'], data['harga']))
    conn.commit()
    conn.close()
    return jsonify({"status": "sukses"})

@app.route('/api/kurangi-stok', methods=['POST'])
def kurangi_stok():
    data = request.json
    nama = data.get('nama')
    conn = get_db_connection()
    item = conn.execute('SELECT * FROM inventory WHERE nama = ?', (nama,)).fetchone()
    
    if item and item['stok'] > 0:
        # Kurangi stok
        conn.execute('UPDATE inventory SET stok = stok - 1 WHERE nama = ?', (nama,))
        # Catat di tabel transaksi
        tgl = datetime.now().strftime('%Y-%m-%d')
        conn.execute('INSERT INTO transaksi (nama_barang, tanggal, jumlah_jual) VALUES (?, ?, 1)', (nama, tgl))
        conn.commit()
        conn.close()
        return jsonify({"status": "sukses"})
    conn.close()
    return jsonify({"status": "gagal"}), 400

# Route untuk ambil laporan omzet
@app.route('/api/laporan')
def laporan():
    conn = get_db_connection()
    # Hitung total penjualan hari ini
    tgl = datetime.now().strftime('%Y-%m-%d')
    total = conn.execute('SELECT SUM(i.harga) FROM transaksi t JOIN inventory i ON t.nama_barang = i.nama WHERE t.tanggal = ?', (tgl,)).fetchone()[0]
    conn.close()
    return jsonify({"omzet": total if total else 0})