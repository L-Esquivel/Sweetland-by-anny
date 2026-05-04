// CONFIGURACIÓN GLOBAL
const API_BASE = "https://sweetland-by-anny-production.up.railway.app";

// --- LÓGICA DEL MENÚ ---
var prevScrollpos = window.pageYOffset;
window.onscroll = function() {
    var currentScrollPos = window.pageYOffset;
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

// --- FUNCIÓN DINÁMICA PARA CARGAR PRODUCTOS ---
async function cargarProductos(categoria) {
    const loader = document.getElementById('loader');
    const galeria = document.getElementById('galeria-productos');
    
    if (!galeria) return;

    try {
        // Llamada al endpoint público de tu Railway
        const response = await fetch(`${API_BASE}/productos/public`);
        const data = await response.json();

        if (data.success) {
            galeria.innerHTML = '';
            
            // Filtramos por la categoría que nos pidan (tortas, postres, etc)
            const filtrados = data.productos.filter(p => p.categoria.toLowerCase() === categoria.toLowerCase());

            if (filtrados.length === 0) {
                galeria.innerHTML = `<p class="no-data">Próximamente más ${categoria} deliciosas...</p>`;
            }

            filtrados.forEach(producto => {
                const div = document.createElement('div');
                div.className = 'producto';
                
                // Si la imagen no carga, ponemos el logo por defecto
                const imgUrl = `${API_BASE}/static/images/${producto.imagen}`;
                
                div.innerHTML = `
                    <div class="img-wrapper">
                        <img src="${imgUrl}" alt="${producto.nombre}" onerror="this.src='assets/logo-principal.png'">
                    </div>
                    <h3>${producto.nombre}</h3>
                    <p class="descripcion">${producto.descripcion}</p>
                    <p class="precio"><strong>$${parseInt(producto.precio).toLocaleString()}</strong></p>
                    <button class="btn-agregar" 
                        onclick="addToCart('${producto.nombre}', ${producto.precio}, '${imgUrl}')">
                        🛒 Agregar al carrito
                    </button>
                `;
                galeria.appendChild(div);
            });
        }
    } catch (error) {
        console.error("Error cargando productos:", error);
        galeria.innerHTML = '<p class="error">Error al conectar con la pastelería. Intenta de nuevo.</p>';
    } finally {
        if (loader) loader.style.display = 'none';
    }
}

// --- CIERRE DE NOTIFICACIÓN ---
function closeNotification() {
    const notification = document.getElementById('cart-notification');
    if (notification) notification.classList.add('hidden');
}