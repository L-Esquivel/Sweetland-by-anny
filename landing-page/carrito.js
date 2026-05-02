// ==================== CONFIGURACIÓN ====================
const API_BASE = 'http://127.0.0.1:5000';

// ==================== CARRITO ====================
let cart = JSON.parse(localStorage.getItem("sweetland_cart")) || [];

// Sesión del cliente (guardada en sessionStorage)
let clienteSession = JSON.parse(sessionStorage.getItem("sweetland_cliente")) || null;

// ==================== SESIÓN ====================

function getCliente() {
  return clienteSession;
}

function setCliente(usuario) {
  clienteSession = usuario;
  sessionStorage.setItem("sweetland_cliente", JSON.stringify(usuario));
  actualizarUICliente();
}

function clearCliente() {
  clienteSession = null;
  sessionStorage.removeItem("sweetland_cliente");
  actualizarUICliente();
}

function actualizarUICliente() {
  const btnLogin    = document.getElementById("btn-login-cliente");
  const btnMisPed   = document.getElementById("btn-mis-pedidos");
  const btnLogout   = document.getElementById("btn-logout-cliente");
  const spanNombre  = document.getElementById("cliente-nombre");

  if (clienteSession) {
    if (btnLogin)   btnLogin.style.display   = "none";
    if (btnMisPed)  btnMisPed.style.display  = "inline-block";
    if (btnLogout)  btnLogout.style.display  = "inline-block";
    if (spanNombre) spanNombre.textContent   = `Hola, ${clienteSession.nombre}`;
  } else {
    if (btnLogin)   btnLogin.style.display   = "inline-block";
    if (btnMisPed)  btnMisPed.style.display  = "none";
    if (btnLogout)  btnLogout.style.display  = "none";
    if (spanNombre) spanNombre.textContent   = "";
  }
}

async function logoutCliente() {
  await fetch(`${API_BASE}/pedidos/public/logout`, {
    method: 'POST',
    credentials: 'include'
  });
  clearCliente();
}

// ==================== CARRITO ====================

function addToCart(name, price, image = null, id_producto = null) {
  const existing = cart.find(item => item.name === name);
  if (existing) {
    existing.qty += 1;
  } else {
    cart.push({
      name,
      price: parseFloat(price),
      qty: 1,
      image,
      id_producto
    });
  }
  localStorage.setItem("sweetland_cart", JSON.stringify(cart));
  updateCartCount();
  showNotification(name, image);
}

function updateCartCount() {
  const totalItems = cart.reduce((sum, item) => sum + item.qty, 0);
  const el = document.getElementById("cart-count");
  if (el) el.textContent = totalItems;
}

function showNotification(productName, imageSrc = null) {
  const notification = document.getElementById("cart-notification");
  if (!notification) return;
  const messageEl = notification.querySelector("p");
  if (messageEl) messageEl.textContent = `¡${productName} añadido!`;
  const imgEl = notification.querySelector("img");
  if (imgEl && imageSrc) imgEl.src = imageSrc;
  notification.classList.remove("hidden");
  setTimeout(() => notification.classList.add("hidden"), 2500);
}

function closeNotification() {
  const notification = document.getElementById("cart-notification");
  if (notification) notification.classList.add("hidden");
}

// ==================== RENDER CARRITO ====================

function renderCart() {
  const cartList    = document.getElementById("cart-list");
  const totalDisplay = document.getElementById("total");
  if (!cartList) return;

  cartList.innerHTML = "";
  let total = 0;

  if (cart.length === 0) {
    cartList.innerHTML = `
      <li class="carrito-vacio">
        <div style="font-size:60px;">🛒</div>
        <p>Tu carrito está vacío.</p>
      </li>`;
    if (totalDisplay) totalDisplay.textContent = "$0";
    return;
  }

  cart.forEach((item, index) => {
    const subtotal = item.price * item.qty;
    total += subtotal;

    const li = document.createElement("li");
    const imgHTML = item.image
      ? `<img class="item-img" src="${item.image}" alt="${item.name}" onerror="this.style.display='none'">`
      : `<div class="item-img-placeholder">🍰</div>`;

    li.innerHTML = `
      ${imgHTML}
      <div class="item-info">
        <span class="item-nombre">${item.name}</span>
        <span class="item-qty">Cantidad: ${item.qty}</span>
      </div>
      <span class="item-precio">$${subtotal.toLocaleString()}</span>
      <button class="btn-eliminar" onclick="removeFromCart(${index})" title="Eliminar">
        <i class="fa-solid fa-xmark"></i>
      </button>
    `;
    cartList.appendChild(li);
  });

  if (totalDisplay) totalDisplay.textContent = `$${total.toLocaleString()}`;
}

function removeFromCart(index) {
  cart.splice(index, 1);
  localStorage.setItem("sweetland_cart", JSON.stringify(cart));
  renderCart();
  updateCartCount();
}

// ==================== GUARDAR PEDIDO EN BD ====================

async function guardarPedidoEnBD() {
  const total = cart.reduce((sum, item) => sum + item.price * item.qty, 0);
  const items = cart.map(item => ({
    id_producto: item.id_producto,
    nombre:      item.name,
    cantidad:    item.qty,
    precio:      item.price,
    subtotal:    item.price * item.qty
  }));

  const body = {
    usuario_id: clienteSession ? clienteSession.id : null,
    telefono:   "",
    direccion:  "",
    total,
    items
  };

  try {
    const res = await fetch(`${API_BASE}/pedidos/public`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      credentials: 'include',
      body: JSON.stringify(body)
    });
    const data = await res.json();
    if (res.ok) {
      console.log(`Pedido guardado en BD con ID: ${data.id_pedido}`);
    } else {
      console.warn("No se pudo guardar el pedido en BD:", data.error);
    }
  } catch (err) {
    console.warn("Error al guardar pedido:", err.message);
  }
}

// ==================== FINALIZAR PEDIDO ====================

async function finalizeOrder() {
  if (cart.length === 0) {
    alert("Tu carrito está vacío.");
    return;
  }

  // Guardar en BD (no bloqueante — si falla, WhatsApp sigue)
  await guardarPedidoEnBD();

  // Armar mensaje de WhatsApp
  let message = "¡Hola Sweetland! Quiero hacer el siguiente pedido:%0A%0A";
  cart.forEach(item => {
    message += `- ${item.qty} x ${item.name} ($${(item.price * item.qty).toLocaleString()})%0A`;
  });
  const total = cart.reduce((sum, item) => sum + item.price * item.qty, 0);
  message += `%0ATotal: $${total.toLocaleString()}`;

  const phone = "573332422608";
  window.open(`https://wa.me/${phone}?text=${message}`, "_blank");
}

// ==================== VACIAR CARRITO ====================

function clearCartAndReload() {
  if (confirm("¿Estás seguro de vaciar el carrito?")) {
    localStorage.removeItem("sweetland_cart");
    cart = [];
    renderCart();
    updateCartCount();
  }
}

// ==================== INIT ====================

document.addEventListener("DOMContentLoaded", () => {
  updateCartCount();
  actualizarUICliente();
});