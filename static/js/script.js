// Show Product Details
function showProductDetails(name, description, price) {
    document.getElementById('product-name').textContent = name;
    document.getElementById('product-description').textContent = description;
    document.getElementById('product-price').textContent = `Price: ${price}`;
    
    // Hide homepage and show product details section
    document.getElementById('home').style.display = 'none';
    document.getElementById('product-details').style.display = 'block';
}

// Add to Cart Functionality
function addToCart() {
    const productName = document.getElementById('product-name').textContent;
    const cartItems = document.querySelector('.cart-items');
    
    // Display item added to the cart
    cartItems.innerHTML = `<p>${productName} added to cart.</p>`;
    
    // Simulate the cart section and show checkout button
    document.getElementById('cart').style.display = 'block';
}

// Filter Products by Category
document.getElementById('category').addEventListener('change', function() {
    const selectedCategory = this.value;
    const products = document.querySelectorAll('.product-list .product');
    
    products.forEach(product => {
        const category = product.getAttribute('data-category');
        
        if (selectedCategory === 'all' || category === selectedCategory) {
            product.style.display = 'block';
        } else {
            product.style.display = 'none';
        }
    });
});

// Search Products by Name
document.getElementById('search-bar').addEventListener('input', function() {
    const query = this.value.toLowerCase();
    const products = document.querySelectorAll('.product-list .product');
    
    products.forEach(product => {
        const productName = product.querySelector('p').textContent.toLowerCase();
        
        if (productName.includes(query)) {
            product.style.display = 'block';
        } else {
            product.style.display = 'none';
        }
    });
});

// Toggle Checkout Section
document.getElementById('checkout-button').addEventListener('click', function() {
    document.getElementById('cart').style.display = 'none';
    document.getElementById('checkout').style.display = 'block';
});

// Admin Panel Toggle
document.getElementById('admin-link').addEventListener('click', function(e) {
    e.preventDefault();
    document.getElementById('admin').style.display = 'block';
});
