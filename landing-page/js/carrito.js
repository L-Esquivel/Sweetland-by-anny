// ==================== CONFIGURACIÓN ====================
// 🚀 URL del backend en producción (Render)
const API_BASE = 'https://precivox-backend.onrender.com';

// El carrito y la sesión los tomamos de localStorage para que sean persistentes
let cart = JSON.parse(localStorage.getItem("sweetland_cart")) || [];

// ==================== FUNCIONES DE CARRITO ====================

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
  actualizarContadorHeader();
  showNotification(name, image);
}

function actualizarContadorHeader() {
  const totalItems = cart.reduce((sum, item) => sum + item.qty, 0);
  const el = document.getElementById("cart-count");
  if (el) el.textContent = totalItems;
}

function renderCart() {
  const cartList = document.getElementById("cart-list");
  const totalDisplay = document.getElementById("total");
  if (!cartList) return;

  cartList.innerHTML = "";
  let total = 0;

  if (cart.length === 0) {
    cartList.innerHTML = `<li class="vacio">Tu carrito está esperando por dulces.</li>`;
    if (totalDisplay) totalDisplay.textContent = "$0";
    return;
  }

  cart.forEach((item, index) => {
    const subtotal = item.price * item.qty;
    total += subtotal;

    const li = document.createElement("li");
    li.className = "cart-item";
    
    // 💡 La imagen ya viene procesada desde script.js (Cloudinary o Local)
    li.innerHTML = `
      <img src="${item.image || 'assets/logo-principal.png'}" onerror="this.src='assets/logo-principal.png'">
      <div class="item-info">
        <span class="item-nombre">${item.name}</span>
        <div class="item-controles">
          <button onclick="cambiarQty(${index}, -1)">-</button>
          <span>${item.qty}</span>
          <button onclick="cambiarQty(${index}, 1)">+</button>
        </div>
      </div>
      <span class="item-precio">$${subtotal.toLocaleString('es-CO')}</span>
      <button class="btn-borrar" onclick="removeFromCart(${index})">🗑️</button>
    `;
    cartList.appendChild(li);
  });

  if (totalDisplay) totalDisplay.textContent = `$${total.toLocaleString('es-CO')}`;
}

function cambiarQty(index, delta) {
  cart[index].qty += delta;
  if (cart[index].qty < 1) {
    cart.splice(index, 1);
  }
  localStorage.setItem("sweetland_cart", JSON.stringify(cart));
  renderCart();
  actualizarContadorHeader();
}

function removeFromCart(index) {
  cart.splice(index, 1);
  localStorage.setItem("sweetland_cart", JSON.stringify(cart));
  renderCart();
  actualizarContadorHeader();
}

// ==================== PROCESAR PEDIDO ====================

async function finalizeOrder() {
  const usuario = JSON.parse(localStorage.getItem("cliente_sweetland"));
  const direccion = document.getElementById("pedido-direccion").value.trim();
  const notas = document.getElementById("pedido-notas").value.trim();
  const loader = document.getElementById("order-loader");

  if (!usuario) {
    alert("Debes iniciar sesión para finalizar el pedido.");
    window.location.href = "mi-cuenta.html";
    return;
  }

  if (!direccion) {
    alert("Por favor ingresa una dirección para la entrega.");
    return;
  }

  if (cart.length === 0) {
    alert("El carrito está vacío.");
    return;
  }

  loader.style.display = "flex";

  try {
    const total = cart.reduce((sum, item) => sum + item.price * item.qty, 0);

    const pedidoCompleto = {
        usuario_id: usuario.id,
        telefono: usuario.telefono || "Sin teléfono",
        direccion: direccion,
        total: total,
        items: cart.map(item => ({
            id_producto: item.id_producto,
            cantidad: item.qty,
            precio: item.price,
            subtotal: item.price * item.qty
        }))
    };

    const response = await fetch(`${API_BASE}/pedidos/public`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      credentials: 'include',
      body: JSON.stringify(pedidoCompleto)
    });

    const data = await response.json();

    if (!response.ok) throw new Error(data.error || "Error al registrar el pedido");

    // 🚀 Todo bien: Abrimos WhatsApp y limpiamos
    abrirWhatsApp(data.id_pedido, usuario.nombre, direccion, notas, total);

    localStorage.removeItem("sweetland_cart");
    cart = [];
    renderCart();
    actualizarContadorHeader();

  } catch (error) {
    alert("Hubo un problema: " + error.message);
  } finally {
    loader.style.display = "none";
  }
}

function abrirWhatsApp(id_pedido, nombreCliente, direccion, notas, total) {
  const nroWA = "573332422608";
  
  // Construimos el mensaje con saltos de línea reales (\n)
  let mensaje = `🎂 *NUEVO PEDIDO # ${id_pedido}* 🎂\n`;
  mensaje += `━━━━━━━━━━━━━━━━━━━━━\n`;
  mensaje += `👤 *Cliente:* ${nombreCliente}\n`;
  mensaje += `📍 *Dirección:* ${direccion}\n`;
  if (notas) mensaje += `📝 *Nota:* ${notas}\n`;
  mensaje += `━━━━━━━━━━━━━━━━━━━━━\n`;
  mensaje += `🛒 *DETALLE DEL PEDIDO:*\n`;
  
  cart.forEach(item => {
    mensaje += `• ${item.qty}x ${item.name} (_$${(item.price * item.qty).toLocaleString('es-CO')}_)\n`;
  });

  mensaje += `━━━━━━━━━━━━━━━━━━━━━\n`;
  mensaje += `💰 *TOTAL A PAGAR: $${total.toLocaleString('es-CO')}*\n\n`;
  mensaje += `_Hola Anny, acabo de realizar este pedido desde la web. Quedo atento a la confirmación para el pago. ✨_`;

  // 💡 CIBERSEGURIDAD: encodeURIComponent asegura que el mensaje sea válido para una URL
  const url = `https://wa.me/${nroWA}?text=${encodeURIComponent(mensaje)}`;
  window.open(url, "_blank");
}

function clearCartAndReload() {
  if (confirm("¿Vaciar todo el carrito?")) {
    localStorage.removeItem("sweetland_cart");
    cart = [];
    renderCart();
    actualizarContadorHeader();
  }
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