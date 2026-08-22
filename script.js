async function prosesStok(kategori, nama) {
    const response = await fetch('/api/kurangi-stok', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({ kategori: kategori, nama: nama })
    });
    
    const data = await response.json();
    
    if(data.status === 'sukses') {
        // Langsung update angka stok di layar
        if(kategori === 'rokok') document.getElementById('stok-rokok').innerText = data.stok_baru;
        if(kategori === 'minyak') document.getElementById('stok-minyak').innerText = data.stok_baru;
    } else {
        alert("Gagal: " + data.pesan);
    }
}