// Usamos un nombre diferente para evitar el error de "Already declared"
const URL_RAILWAY = "https://sweetland-by-anny-production.up.railway.app";

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

// --- 2. FUNCIÓN PARA OCULTAR EL LOADER ---
function ocultarLoader() {
    const loader = document.getElementById('loader');
    if (loader) {
        // Un pequeño delay para que no sea tan brusco
        setTimeout(() => {
            loader.style.display = 'none';
        }, 300);
    }
}

// --- 3. CARGA DINÁMICA DE PRODUCTOS ---
async function cargarProductos(categoria) {
    const galeria = document.getElementById('galeria-productos');
    
    // Si no hay galería en esta página, solo quitamos el loader y salimos
    if (!galeria) {
        ocultarLoader();
        return;
    }

    try {
        console.log(`Buscando productos de la categoría: ${categoria}`);
        
        // Usamos la nueva constante URL_RAILWAY
        const response = await fetch(`${URL_RAILWAY}/productos/public`);
        const data = await response.json();

        if (data.success) {
            galeria.innerHTML = '';
            
            // Filtramos productos por categoría
            const filtrados = data.productos.filter(p => 
                p.categoria && p.categoria.toLowerCase() === categoria.toLowerCase()
            );

            if (filtrados.length === 0) {
                galeria.innerHTML = `<p class="no-data">Próximamente más ${categoria} deliciosas...</p>`;
            } else {
                filtrados.forEach(producto => {
                    const div = document.createElement('div');
                    div.className = 'producto';
                    const imgUrl = `${URL_RAILWAY}/static/images/${producto.imagen}`;
                    
                    div.innerHTML = `
                        <div class="img-wrapper">
                            <img src="${imgUrl}" alt="${producto.nombre}" onerror="this.src='assets/logo-principal.png'">
                        </div>
                        <h3>${producto.nombre}</h3>
                        <p class="descripcion">${producto.descripcion}</p>
                        <p class="precio"><strong>$${parseInt(producto.precio).toLocaleString('es-CO')}</strong></p>
                        <button class="btn-agregar" 
                            onclick="addToCart('${producto.nombre}', ${producto.precio}, '${imgUrl}', ${producto.id_producto})">
                            🛒 Agregar al carrito
                        </button>
                    `;
                    galeria.appendChild(div);
                });
            }
        }
    } catch (error) {
        console.error("Error cargando productos:", error);
        galeria.innerHTML = '<p class="error">Error al conectar con el servidor.</p>';
    } finally {
        // El bloque finally se ejecuta SIEMPRE, incluso si hay error
        // Esto garantiza que el loader desaparezca
        ocultarLoader();
    }
}

// --- 4. FUNCIÓN PARA CERRAR NOTIFICACIONES ---
function closeNotification() {
    const notification = document.getElementById('cart-notification');
    if (notification) notification.classList.add('hidden');
}