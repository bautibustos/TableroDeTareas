async function loadTasks() {
    try {
        const response = await fetch('/api/tasks');
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
    } 
    catch (e) {
        console.error('Error:', e);
    }
}

setInterval(loadTasks, 30000);
loadTasks();