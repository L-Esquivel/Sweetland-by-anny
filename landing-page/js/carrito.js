// ==================== CONFIGURACIÓN ====================
const API_BASE = 'https://sweetland-by-anny-production.up.railway.app';

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
}

function removeFromCart(index) {
  cart.splice(index, 1);
  localStorage.setItem("sweetland_cart", JSON.stringify(cart));
  renderCart();
  actualizarContadorHeader();
}

// ==================== PROCESAR PEDIDO (Guardar + WhatsApp) ====================

async function finalizeOrder() {
  const usuario = JSON.parse(localStorage.getItem("cliente_sweetland"));
  const direccion = document.getElementById("pedido-direccion").value.trim();
  const notas = document.getElementById("pedido-notas").value.trim();
  const loader = document.getElementById("order-loader");

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

    // 1. Crear la cabecera del pedido
    const resPedido = await fetch(`${API_BASE}/pedidos/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      credentials: 'include',
      body: JSON.stringify({
        usuario_id: usuario.id_usuario,
        telefono: usuario.telefono || "Sin teléfono",
        direccion: direccion,
        total: total
      })
    });

    const dataPedido = await resPedido.json();
    if (!resPedido.ok) throw new Error(dataPedido.error || "Error al crear pedido.");

    const id_pedido = dataPedido.id_pedido;

    // 2. Guardar cada producto en el detalle del pedido
    for (const item of cart) {
      await fetch(`${API_BASE}/pedidos/${id_pedido}/agregar_detalle`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({
          producto_id: item.id_producto,
          cantidad: item.qty,
          subtotal: item.price * item.qty
        })
      });
    }

    // 3. Abrir WhatsApp con el resumen
    abrirWhatsApp(id_pedido, direccion, notas, total);

    // 4. Limpiar carrito
    localStorage.removeItem("sweetland_cart");
    cart = [];
    renderCart();

  } catch (error) {
    console.error(error);
    alert("Hubo un problema al guardar tu pedido: " + error.message);
  } finally {
    loader.style.display = "none";
  }
}

function abrirWhatsApp(id_pedido, direccion, notas, total) {
  const nroWA = "573332422608";
  let mensaje = `✨ *NUEVO PEDIDO # ${id_pedido}* ✨%0A`;
  mensaje += `👤 *Cliente:* ${JSON.parse(localStorage.getItem("cliente_sweetland")).nombre}%0A`;
  mensaje += `📍 *Dirección:* ${direccion}%0A`;
  if (notas) mensaje += `📝 *Nota:* ${notas}%0A%0A`;
  
  mensaje += `🛒 *Resumen:*%0A`;
  cart.forEach(item => {
    mensaje += `- ${item.qty}x ${item.name} ($${(item.price * item.qty).toLocaleString('es-CO')})%0A`;
  });

  mensaje += `%0A💰 *TOTAL:* $${total.toLocaleString('es-CO')}%0A%0A`;
  mensaje += `_Por favor, confírmame disponibilidad para realizar el pago._`;

  window.open(`https://wa.me/${nroWA}?text=${mensaje}`, "_blank");
}

function clearCartAndReload() {
  if (confirm("¿Vaciar todo el carrito?")) {
    localStorage.removeItem("sweetland_cart");
    cart = [];
    renderCart();
    actualizarContadorHeader();
  }
}