/*
 * Welcome to your app's main JavaScript file!
 *
 * We recommend including the built version of this JavaScript file
 * (and its CSS file) in your base layout (base.html.twig).
 */

// any CSS you import will output into a single css file (app.css in this case)
import 'bootstrap';
import 'bootstrap/dist/css/bootstrap.min.css';
import './styles/app.css';


document.addEventListener('click', function(e) {
    if (e.target.classList.contains('remove-city-btn')) {
        const card = e.target.closest('.city-card');
        if (!card) return;

        const cityId = card.dataset.id;
        // 1️⃣ Eliminar del localStorage
        let cities = JSON.parse(localStorage.getItem('cities') || '[]');
        cities = cities.filter(c => c.id !== parseInt(cityId));
        localStorage.setItem('cities', JSON.stringify(cities));

        // 2️⃣ Eliminar del DOM
        card.remove();

        // 3️⃣ Opcional: mostrar mensaje si queda vacío
        const container = document.getElementById('cities-container');
        if (cities.length === 0) {
            container.innerHTML = '<p id="empty-msg">No hay ciudades para mostrar.</p>';
        }
        window.location.reload();
    }
});

// --- Helpers para manejar LocalStorage ---
    function getStoredCities() {
    return JSON.parse(localStorage.getItem('cities') || '[]');
}

    function saveCity(city) {
    let cities = getStoredCities();
    cities.push(city);
    localStorage.setItem('cities', JSON.stringify(cities));
}

    async function renderCities() {
    const container = document.getElementById('cities-container');
    const cities = getStoredCities();

    if (cities.length === 0) {
    container.innerHTML = '<p id="empty-msg">No hay ciudades para mostrar.</p>';
    return;
}

    try {
    const response = await fetch('/api/render-cities', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(cities),
});

    if (!response.ok) {
    console.error("Status:", response.status);
    throw new Error('Error al renderizar las ciudades');
}

    const data = await response.json();
    container.innerHTML = data.html;
} catch (err) {
    console.error(err);
    container.innerHTML = '<p class="text-danger">Error al renderizar ciudades.</p>';
}
}

    // --- Inicializar las ciudades desde localStorage al cargar ---
    document.addEventListener('DOMContentLoaded', () => {
    renderCities();

    const form = document.querySelector('#search-form');
    form.addEventListener('submit', async (e) => {
    e.preventDefault();

    const query = form.querySelector('input[name="q"]').value.trim();
    if (!query) return;

    // Revisar si ya existe en localStorage
    const stored = getStoredCities();
    if (stored.some(c => c.city.toLowerCase() === query.toLowerCase())) {
    alert('Esa ciudad ya está en la lista.');
    return;
}

    try {
    const response = await fetch(`/api/weather/search?q=${encodeURIComponent(query)}`);
    if (!response.ok) {
    alert('No se pudo obtener el clima de esa ciudad.');
    return;
}

    const city = await response.json();
    saveCity(city);
    renderCities();
} catch (err) {
    console.error(err);
    alert('Error de conexión con el servidor.');
}
});
});

document.addEventListener('DOMContentLoaded', function() {
    // Botón de Telegram
    const telegramBtn = document.getElementById('telegram-btn');
    if (telegramBtn) {
        telegramBtn.addEventListener('click', function() {
            subscribeToTelegram();
        });
    }

    // Botón de WhatsApp
    const whatsappBtn = document.getElementById('whatsapp-btn');
    if (whatsappBtn) {
        whatsappBtn.addEventListener('click', function() {
            subscribeToWhatsApp();
        });
    }
});

function subscribeToTelegram() {
    console.log('Suscribiendo a Telegram...');
    // Reemplaza con tu enlace de Telegram
    window.open('https://t.me/tu_canal', '_blank');
}

function subscribeToWhatsApp() {
    console.log('Suscribiendo a WhatsApp...');
    // Reemplaza con tu número de WhatsApp (formato internacional sin + ni espacios)
    const phoneNumber = '5491234567890'; // Ejemplo: Argentina +54 9 123 456 7890
    const message = 'Hola, me interesa suscribirme'; // Mensaje opcional
    const whatsappUrl = `https://wa.me/${phoneNumber}?text=${encodeURIComponent(message)}`;
    window.open(whatsappUrl, '_blank');
}
