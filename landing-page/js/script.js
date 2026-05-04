// CONFIGURACIÓN GLOBAL
const API_BASE = "https://sweetland-by-anny-production.up.railway.app";

// --- 1. LÓGICA DEL MENÚ (Scroll) ---
let prevScrollpos = window.pageYOffset;
window.onscroll = function() {
    let currentScrollPos = window.pageYOffset;
    const menu = document.getElementById("menu");
    if (menu) {
        if (prevScrollpos > currentScrollPos) {
            menu.style.top = "0";
        } else {
            menu.style.top = "-80px";
        }
    }
    prevScrollpos = currentScrollPos;
}

// --- 2. FUNCIÓN PARA OCULTAR CUALQUIER LOADER ---
function ocultarLoader() {
    const loader = document.getElementById('loader');
    if (loader) {
        loader.style.opacity = "0";
        setTimeout(() => {
            loader.style.display = 'none';
        }, 500); // Desvanecimiento suave
    }
}

// --- 3. CARGA DINÁMICA DE PRODUCTOS ---
async function cargarProductos(categoria) {
    const galeria = document.getElementById('galeria-productos');
    if (!galeria) {
        ocultarLoader();
        return;
    }

    try {
        const response = await fetch(`${API_BASE}/productos/public`);
        const data = await response.json();

        if (data.success) {
            galeria.innerHTML = '';
            const filtrados = data.productos.filter(p => p.categoria.toLowerCase() === categoria.toLowerCase());

            if (filtrados.length === 0) {
                galeria.innerHTML = `<p class="no-data">Próximamente más ${categoria} deliciosas...</p>`;
            } else {
                filtrados.forEach(producto => {
                    const div = document.createElement('div');
                    div.className = 'producto';
                    const imgUrl = `${API_BASE}/static/images/${producto.imagen}`;
                    
                    div.innerHTML = `
                        <div class="img-wrapper">
                            <img src="${imgUrl}" alt="${producto.nombre}" onerror="this.src='assets/logo-principal.png'">
                        </div>
                        <h3>${producto.nombre}</h3>
                        <p class="descripcion">${producto.descripcion}</p>
                        <p class="precio"><strong>$${parseInt(producto.precio).toLocaleString('es-CO')}</strong></p>
                        <button class="btn-agregar" 
                            onclick="addToCart('${producto.nombre}', ${producto.precio}, '${imgUrl}', ${producto.id_producto})">
                            🛒 Agregar
                        </button>
                    `;
                    galeria.appendChild(div);
                });
            }
        }
    } catch (error) {
        console.error("Error:", error);
        galeria.innerHTML = '<p class="error">Error al cargar productos.</p>';
    } finally {
        // Pase lo que pase, ocultamos el loader
        ocultarLoader();
    }
}

// Función para cerrar notificaciones
function closeNotification() {
    const notification = document.getElementById('cart-notification');
    if (notification) notification.classList.add('hidden');
}