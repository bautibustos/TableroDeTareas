async function loadTasks() {
const board = document.getElementById('board');

try {
    const response = await fetch('/api/tasks');
    const tasks = await response.json();
    
    board.innerHTML = ''; // Limpiar pizarra

    tasks.forEach(task => {
        const card = document.createElement('div');
        card.className = 'note-card';
        
        // Formatear fecha
        const fecha = new Date(task.fecha_creacion).toLocaleString();

        card.innerHTML = `
            <button class="close-btn" onclick="closeTask(${task.id_task})">
                <span class="material-symbols-outlined">close</span>
            </button>
            <div class="note-content">
                <h3 class="note-title">ID Usuario: ${task.creador}</h3>
                <p class="note-text">${task.descripcion}</p>
                <div class="note-footer">
                    Creada: ${fecha}
                </div>
            </div>
        `;
        board.appendChild(card);
    });
} catch (error) {
    console.error("Error cargando tareas:", error);
}


}

async function closeTask(id) {
// Aquí irá la lógica del UPDATE cuando la definamos
console.log("Cerrando tarea:", id);
}

// Carga inicial
loadTasks();
// Recarga automática cada 30 segundos
setInterval(loadTasks, 30000);