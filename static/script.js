let filtroActual = "todas";
let tareasCache = [];
let textoBusqueda = "";
let ordenActual = "reciente"; // ← nueva

async function cargarTareas() {
    const res = await fetch("/tareas");
    tareasCache = await res.json();
    renderizarTareas(tareasCache);
}

function renderizarTareas(tareas) {
    const lista = document.getElementById("lista-tareas");
    lista.innerHTML = "";

    const filtradas = tareasFiltradas(tareas);

    // Agrupar por categoría
    const categorias = {
        trabajo: { label: "💼 Trabajo", tareas: [] },
        estudios: { label: "📚 Estudios", tareas: [] },
        personal: { label: "🏠 Personal", tareas: [] }
    };

    filtradas.forEach(t => {
        if (categorias[t.categoria]) {
            categorias[t.categoria].tareas.push(t);
        }
    });

    // Mensaje si no hay tareas
    const hayTareas = filtradas.length > 0;
    if (!hayTareas) {
        const vacio = document.createElement("li");
        vacio.classList.add("vacio");
        vacio.textContent = "No hay tareas aquí todavía 👀";
        lista.appendChild(vacio);
        actualizarContador(tareas);
        return;
    }

    // Renderizar grupos
    Object.entries(categorias).forEach(([key, grupo]) => {
        if (grupo.tareas.length === 0) return;

        const seccion = document.createElement("li");
        seccion.classList.add("categoria-header");
        seccion.textContent = grupo.label;
        lista.appendChild(seccion);

        grupo.tareas.forEach(t => {
            const li = document.createElement("li");
            li.setAttribute("data-id", t.id);
            if (t.completada) li.classList.add("completada");

            // Fecha
            let fechaTexto = "";
            if (t.fecha_limite) {
                const [year, month, day] = t.fecha_limite.split("-");
                fechaTexto = `<span class="fecha">📅 ${day}/${month}/${year}</span>`;
            }

            // Prioridad
            const etiquetas = { alta: "🔴 Alta", media: "🟡 Media", baja: "🟢 Baja" };
            const etiquetaPrioridad = `<span class="prioridad prioridad-${t.prioridad}">${etiquetas[t.prioridad]}</span>`;

            li.innerHTML = `
                <span class="titulo">${t.titulo}</span>
                ${etiquetaPrioridad}
                ${fechaTexto}
                ${!t.completada ? `
                    <button class="btn-completar" onclick="completar(${t.id})">✓ Listo</button>
                    <button class="btn-editar" onclick="editar(${t.id}, '${t.titulo.replace(/'/g, "\\'")}')">✏️ Editar</button>
                ` : ""}
                <button class="btn-eliminar" onclick="eliminar(${t.id})">🗑</button>
            `;
            lista.appendChild(li);
        });
    });

    actualizarContador(tareas);
}

async function agregarTarea() {
    const input = document.getElementById("nueva-tarea");
    const fecha = document.getElementById("fecha-limite");
    const prioridad = document.getElementById("prioridad");
    const categoria = document.getElementById("categoria");
    const titulo = input.value.trim();
    if (!titulo) return;

    await fetch("/tareas", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            titulo,
            fecha_limite: fecha.value || null,
            prioridad: prioridad.value,
            categoria: categoria.value
        })
    });

    input.value = "";
    fecha.value = "";
    prioridad.value = "media";
    categoria.value = "personal";
    cargarTareas();
}

async function completar(id) {
    await fetch(`/tareas/${id}`, { method: "PUT" });
    cargarTareas();
}

async function eliminar(id) {
    await fetch(`/tareas/${id}`, { method: "DELETE" });
    cargarTareas();
}

// Agregar con Enter
document.addEventListener("DOMContentLoaded", () => {
    cargarTareas();
    document.getElementById("nueva-tarea").addEventListener("keypress", e => {
        if (e.key === "Enter") agregarTarea();
    });
});

async function editar(id, tituloActual) {
    const li = document.querySelector(`[data-id="${id}"]`);
    const spanTitulo = li.querySelector(".titulo");

    // Convertir el título en un input editable
    const input = document.createElement("input");
    input.type = "text";
    input.value = tituloActual;
    input.classList.add("input-editar");
    spanTitulo.replaceWith(input);
    input.focus();

    // Botón para guardar
    const btnGuardar = li.querySelector(".btn-editar");
    btnGuardar.textContent = "💾 Guardar";
    btnGuardar.onclick = async () => {
        const nuevoTitulo = input.value.trim();
        if (!nuevoTitulo) return;
        await fetch(`/tareas/${id}`, {
            method: "PATCH",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ titulo: nuevoTitulo })
        });
        cargarTareas();
    };

    // Guardar también con Enter
    input.addEventListener("keypress", (e) => {
        if (e.key === "Enter") btnGuardar.click();
    });
}

function actualizarContador(tareas) {
    const total = tareas.length;
    const completadas = tareas.filter(t => t.completada).length;
    const pendientes = total - completadas;

    document.getElementById("total").textContent = total;
    document.getElementById("pendientes").textContent = pendientes;
    document.getElementById("completadas").textContent = completadas;
}

function cambiarFiltro(filtro, btn) {
    filtroActual = filtro;

    // Actualizar botón activo
    document.querySelectorAll(".btn-filtro").forEach(b => b.classList.remove("activo"));
    btn.classList.add("activo");

    renderizarTareas(tareasCache);
}

function tareasFiltradas(tareas) {
    let resultado = tareas;

    // Filtro por estado
    if (filtroActual === "pendientes") resultado = resultado.filter(t => !t.completada);
    if (filtroActual === "completadas") resultado = resultado.filter(t => t.completada);

    // Filtro por búsqueda
    if (textoBusqueda) {
        resultado = resultado.filter(t =>
            t.titulo.toLowerCase().includes(textoBusqueda)
        );
    }

    // Ordenar
    return ordenarTareas(resultado);
}

function buscar(texto) {
    textoBusqueda = texto.toLowerCase().trim();
    renderizarTareas(tareasCache);
}

function cambiarOrden(orden) {
    ordenActual = orden;
    renderizarTareas(tareasCache);
}

function ordenarTareas(tareas) {
    const prioridadValor = { alta: 3, media: 2, baja: 1 };

    return [...tareas].sort((a, b) => {
        if (ordenActual === "nombre") {
            return a.titulo.localeCompare(b.titulo);
        }
        if (ordenActual === "prioridad") {
            return prioridadValor[b.prioridad] - prioridadValor[a.prioridad];
        }
        if (ordenActual === "fecha") {
            if (!a.fecha_limite) return 1;
            if (!b.fecha_limite) return -1;
            return new Date(a.fecha_limite) - new Date(b.fecha_limite);
        }
        // Por defecto: más reciente primero
        return b.id - a.id;
    });
}