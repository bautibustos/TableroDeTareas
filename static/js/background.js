const FALLBACK_COLOR = '#6CAEE5';
const CHANGE_INTERVAL = 30000; // 30 segundos

let backgrounds = [];
let currentIndex = 0;

function applyBackground() {
    if (backgrounds.length === 0) {
        document.body.style.backgroundImage = 'none';
        document.body.style.backgroundColor = FALLBACK_COLOR;
        return;
    }
    document.body.style.backgroundColor = '';
    document.body.style.backgroundImage = `url('${backgrounds[currentIndex]}')`;
    currentIndex = (currentIndex + 1) % backgrounds.length;
}

async function loadBackgrounds() {
    try {
        const response = await fetch('/api/backgrounds');
        backgrounds = await response.json();
    } catch (e) {
        console.error('Error al cargar los fondos:', e);
        backgrounds = [];
    }
    applyBackground();
}

loadBackgrounds();
setInterval(applyBackground, CHANGE_INTERVAL);
