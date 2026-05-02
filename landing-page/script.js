var prevScrollpos = window.pageYOffset;
window.onscroll = function() {
var currentScrollPos = window.pageYOffset;
  if (prevScrollpos > currentScrollPos) {
    document.getElementById("menu").style.top = "0";
  } else {
    document.getElementById("menu").style.top = "-80px";
  }
  prevScrollpos = currentScrollPos;
}

// Mostrar pantalla de carga antes de mostrar el contenido torta
window.addEventListener("load", function () {
  const loader = document.getElementById("loader");
  const contenido = document.getElementById("contenido-torta");

  if (loader && contenido) {
    // Oculta el loader después de 1.5 segundos (ajustable)
    setTimeout(() => {
      loader.style.display = "none";
      contenido.style.display = "block";
    }, 1500);
  }
});

// Mostrar pantalla de carga antes de mostrar el contenido postre
window.addEventListener("load", function () {
  const loader = document.getElementById("loader");
  const contenido = document.getElementById("contenido-postre");

  if (loader && contenido) {
    // Oculta el loader después de 1.5 segundos (ajustable)
    setTimeout(() => {
      loader.style.display = "none";
      contenido.style.display = "block";
    }, 1500);
  }
});

// Mostrar pantalla de carga antes de mostrar el contenido detalles
window.addEventListener("load", function () {
  const loader = document.getElementById("loader");
  const contenido = document.getElementById("contenido-detalles");

  if (loader && contenido) {
    // Oculta el loader después de 1.5 segundos (ajustable)
    setTimeout(() => {
      loader.style.display = "none";
      contenido.style.display = "block";
    }, 1500);
  }
});