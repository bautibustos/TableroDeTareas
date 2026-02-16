async function loadTasks() {
    try {
        const response = await fetch('/api/tasks');
        const tasks = await response.json();
        console.log('Tareas cargadas:', tasks);  // Debug
        const board = document.getElementById('board');
        board.innerHTML = '';

        tasks.forEach(task => {
            const card = document.createElement('div');
            card.className = 'note-card';
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


            card.innerHTML = `
                <div class="header">
                    <div class="task-id">#${task.id_task}</div>
                    <div class="badges"> 
                        <span class="badge ${priorityClass}">
                            <span class="dot"></span> ${priorityLabel}
                        </span>
                    </div>
                </div>
                <div class="creator"><b>${task.creador}</b></div>
                <p class="note-text">${task.descripcion}</p>
                <p class="note-text"><b>${fecha}</b></p>
            `;
            board.appendChild(card);
        });
    } catch (e) {
        console.error('Error:', e);
    }
}

setInterval(loadTasks, 30000);
loadTasks();