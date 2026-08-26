const REFRESH_SECONDS = 30;
const FETCH_TIMEOUT_MS = 10000;
let secondsUntilRefresh = REFRESH_SECONDS;
let backendDown = false;

function renderUpdateCounter() {
    const counterEl = document.getElementById('update-counter');
    if (!counterEl) return;

    if (backendDown) {
        counterEl.textContent = '⚠ Sistema caído: sin respuesta del servidor';
        counterEl.classList.add('update-counter-error');
    } else {
        counterEl.textContent = `Actualiza en ${secondsUntilRefresh}s`;
        counterEl.classList.remove('update-counter-error');
    }
}

function tickUpdateCounter() {
    if (backendDown) return; // congelado hasta que vuelva a responder
    secondsUntilRefresh = Math.max(0, secondsUntilRefresh - 1);
    renderUpdateCounter();
}

async function loadTasks() {
    try {
        const response = await fetch('/api/tasks', { signal: AbortSignal.timeout(FETCH_TIMEOUT_MS) });
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }
        const tasks = await response.json();
        console.log('Tareas cargadas:', tasks);  // Debug
        const board = document.getElementById('board');
        board.innerHTML = '';

        tasks.forEach(task => {
            const card = document.createElement('div');
            const fecha = new Date(task.fecha_creacion).toLocaleString('es-AR');

            let priorityClass = '';
            let priorityLabel = '';

            switch (task.prioridad) {
                case 1:
                    priorityClass = 'priority-high';
                    priorityLabel = 'Alta';
                    break;
                case 2:
                    priorityClass = 'priority-medium';
                    priorityLabel = 'Media';
                    break;
                case 3:
                    priorityClass = 'priority-low';
                    priorityLabel = 'Baja';
                    break;
            }

            card.className = `note-card ${priorityClass}`;

            card.innerHTML = `
                <div class="header">
                    <div class="task-id">#${task.id_task}</div>
                    <div class="creator"><b>${task.creador}</b></div>
                    <div class="badges">
                        <span class="badge ${priorityClass}">
                            <span class="dot"></span> ${priorityLabel}
                        </span>
                    </div>
                </div>
                <p class="description-text">${task.descripcion}</p>
                <div class="note-text" style="display: flex; justify-content: space-between; align-items: center;">
                    <b class="date-text">${fecha}</b>
                    <span class="assigned">Asignado a: ${task.assign}</span>
                </div>
            `;
            board.appendChild(card);
        });
        backendDown = false;
    }
    catch (e) {
        console.error('Error:', e);
        backendDown = true;
    }
    finally {
        secondsUntilRefresh = REFRESH_SECONDS;
        renderUpdateCounter();
    }
}

setInterval(loadTasks, REFRESH_SECONDS * 1000);
setInterval(tickUpdateCounter, 1000);
loadTasks();