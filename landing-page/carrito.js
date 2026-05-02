// ==================== CARRITO DE COMPRAS ====================

let cart = JSON.parse(localStorage.getItem("sweetland_cart")) || [];

// Agregar al carrito
function addToCart(name, price, image = null) {
  const existing = cart.find(item => item.name === name);

  if (existing) {
    existing.qty += 1;
  } else {
    cart.push({ 
      name, 
      price: parseFloat(price), 
      qty: 1,
      image: image 
    });
  }

  localStorage.setItem("sweetland_cart", JSON.stringify(cart));
  updateCartCount();
  showNotification(name, image);
}

// Actualizar contador del carrito
function updateCartCount() {
  const totalItems = cart.reduce((sum, item) => sum + item.qty, 0);
  const cartCountEl = document.getElementById("cart-count");
  if (cartCountEl) cartCountEl.textContent = totalItems;
}

// Mostrar notificación con imagen
function showNotification(productName, imageSrc = null) {
  const notification = document.getElementById("cart-notification");
  if (!notification) return;

  const messageEl = notification.querySelector("p");
  messageEl.textContent = `¡${productName} añadido!`;

  const imgEl = notification.querySelector("img");
  if (imgEl && imageSrc) {
    imgEl.src = imageSrc;
  }

  notification.classList.remove("hidden");

  setTimeout(() => {
    notification.classList.add("hidden");
  }, 2500);
}

function closeNotification() {
  const notification = document.getElementById("cart-notification");
  if (notification) notification.classList.add("hidden");
}

// Renderizar carrito
function renderCart() {
  const cartList = document.getElementById("cart-list");
  const totalDisplay = document.getElementById("total");

  if (!cartList) return;

  cartList.innerHTML = "";
  let total = 0;

  if (cart.length === 0) {
    cartList.innerHTML = "<li style='text-align:center; padding:20px;'>Tu carrito está vacío.</li>";
    totalDisplay.textContent = "$0";
    return;
  }

  cart.forEach((item, index) => {
    const li = document.createElement("li");
    li.style.marginBottom = "10px";
    li.innerHTML = `
      ${item.qty} x ${item.name} 
      <strong>$${(item.price * item.qty).toLocaleString()}</strong>
      <button onclick="removeFromCart(${index})" style="color:red; margin-left:15px; font-size:0.9em;">Eliminar</button>
    `;
    cartList.appendChild(li);
    total += item.price * item.qty;
  });

  totalDisplay.textContent = `$${total.toLocaleString()}`;
}

// Eliminar producto del carrito
function removeFromCart(index) {
  cart.splice(index, 1);
  localStorage.setItem("sweetland_cart", JSON.stringify(cart));
  renderCart();
  updateCartCount();
}

// Enviar pedido por WhatsApp
function finalizeOrder() {
  if (cart.length === 0) {
    alert("Tu carrito está vacío.");
    return;
  }

  let message = "¡Hola Sweetland! Quiero hacer el siguiente pedido:%0A%0A";
  cart.forEach(item => {
    message += `- ${item.qty} x ${item.name} ($${(item.price * item.qty).toLocaleString()})%0A`;
  });

  const total = cart.reduce((sum, item) => sum + item.price * item.qty, 0);
  message += `%0ATotal: $${total.toLocaleString()}`;

  const phone = "573332422608";
  const url = `https://wa.me/${phone}?text=${message}`;
  window.open(url, "_blank");
}

// Vaciar carrito
function clearCartAndReload() {
  if (confirm("¿Estás seguro de vaciar el carrito?")) {
    localStorage.removeItem("sweetland_cart");
    cart = [];
    renderCart();
    updateCartCount();
  }
}

// Inicializar
document.addEventListener("DOMContentLoaded", () => {
  updateCartCount();
});