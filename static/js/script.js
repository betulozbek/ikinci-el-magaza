// Sepete ürün eklemek için fonksiyon
function addToCart(productId) {
    // Ürün adedi
    const quantity = document.getElementById(`urun_adet_${productId}`).value;

    // AJAX isteği gönderiyoruz
    fetch(`/add_to_cart/${productId}/${quantity}`, {
        method: 'POST',  // POST metodu kullanıyoruz
        headers: {
            'Content-Type': 'application/json'
        }
    })
    .then(response => response.json())
    .then(data => {
        // Sepete ekleme başarılıysa mesaj gösteriyoruz
        alert(data.message);
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Bir hata oluştu!');
    });
}
