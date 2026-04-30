// ──────────────────────────────────────────────────────────────
// script.js — Lógica del frontend
// Maneja todas las interacciones del usuario con la interfaz:
// cargar, crear, editar, completar y eliminar tareas.
// También maneja filtros, búsqueda y ordenamiento.
//
// Orden del archivo:
// 1. Variables globales
// 2. Funciones de utilidad
// 3. Funciones de renderizado
// 4. Funciones de acciones (CRUD)
// 5. Funciones de filtros, búsqueda y orden
// 6. Inicialización (DOMContentLoaded)
// ──────────────────────────────────────────────────────────────


// ── 1. Variables globales ──────────────────────────────────────

// Estado actual del filtro de tareas (todas, pendientes, completadas)
let filtroActual = "todas";

// Cache de tareas — evita llamadas innecesarias al backend
// Se actualiza cada vez que se carga o modifica una tarea
let tareasCache = [];

// Texto actual en el buscador para filtrar tareas
let textoBusqueda = "";

// Criterio actual de ordenamiento de las tareas
let ordenActual = "reciente";


// ── 2. Funciones de utilidad ───────────────────────────────────

function actualizarContador(tareas) {
    /*
     * Actualiza los números del contador superior en tiempo real.
     * Recibe el arreglo completo de tareas (sin filtrar) para
     * mostrar los totales reales, no los filtrados.
     */
    const total = tareas.length;
    const completadas = tareas.filter(t => t.completada).length;
    const pendientes = total - completadas;

    document.getElementById("total").textContent = total;
    document.getElementById("pendientes").textContent = pendientes;
    document.getElementById("completadas").textContent = completadas;
}

function mostrarNotificacion(mensaje, tipo) {
    /*
     * Muestra una notificación temporal en la esquina inferior derecha.
     * tipo puede ser "exito" o "error" — cambia el color del mensaje.
     * Desaparece automáticamente después de 3 segundos.
     */
    const notif = document.createElement("div");
    notif.textContent = mensaje;
    notif.classList.add("notificacion", `notificacion-${tipo}`);
    document.body.appendChild(notif);
    setTimeout(() => notif.remove(), 3000);
}

function tareasFiltradas(tareas) {
    /*
     * Aplica los filtros activos al arreglo de tareas y retorna
     * el resultado. Los filtros se aplican en este orden:
     * 1. Filtro por estado (todas, pendientes, completadas)
     * 2. Filtro por texto de búsqueda
     * 3. Ordenamiento
     */
    let resultado = tareas;

    // Filtro por estado
    if (filtroActual === "pendientes") resultado = resultado.filter(t => !t.completada);
    if (filtroActual === "completadas") resultado = resultado.filter(t => t.completada);

    // Filtro por texto de búsqueda — busca en el título de la tarea
    if (textoBusqueda) {
        resultado = resultado.filter(t =>
            t.titulo.toLowerCase().includes(textoBusqueda)
        );
    }

    // Aplicar ordenamiento y retornar resultado final
    return ordenarTareas(resultado);
}

function ordenarTareas(tareas) {
    /*
     * Ordena el arreglo de tareas según el criterio actual.
     * Usa spread [...tareas] para no mutar el arreglo original.
     *
     * sort() compara de dos en dos (a y b):
     * - resultado > 0 → b va primero
     * - resultado < 0 → a va primero
     * - resultado = 0 → quedan igual
     */
    const prioridadValor = { alta: 3, media: 2, baja: 1 };

    return [...tareas].sort((a, b) => {
        if (ordenActual === "nombre") {
            // localeCompare respeta tildes y ñ en español
            return a.titulo.localeCompare(b.titulo);
        }
        if (ordenActual === "prioridad") {
            // Restamos los valores numéricos — mayor valor va primero
            return prioridadValor[b.prioridad] - prioridadValor[a.prioridad];
        }
        if (ordenActual === "fecha") {
            // Las tareas sin fecha van al final
            if (!a.fecha_limite) return 1;
            if (!b.fecha_limite) return -1;
            // Las fechas más próximas van primero
            return new Date(a.fecha_limite) - new Date(b.fecha_limite);
        }
        // Por defecto: más reciente primero (id más alto = más reciente)
        return b.id - a.id;
    });
}


// ── 3. Funciones de renderizado ────────────────────────────────

async function cargarTareas() {
    /*
     * Obtiene todas las tareas del usuario desde el backend
     * y las guarda en tareasCache para evitar llamadas repetidas.
     * Luego llama a renderizarTareas para mostrarlas.
     */
    try {
        const res = await fetch("/tareas");
        tareasCache = await res.json();
        renderizarTareas(tareasCache);
    } catch (error) {
        mostrarNotificacion("Error al cargar las tareas", "error");
    }
}

function renderizarTareas(tareas) {
    /*
     * Renderiza la lista de tareas en el DOM aplicando los
     * filtros y ordenamiento actuales.
     * Las agrupa por categoría (Trabajo, Estudios, Personal).
     * Si no hay tareas muestra un mensaje vacío.
     */
    const lista = document.getElementById("lista-tareas");
    lista.innerHTML = "";

    // Aplicar filtros, búsqueda y ordenamiento
    const filtradas = tareasFiltradas(tareas);

    // Estructura de categorías para agrupar las tareas
    const categorias = {
        trabajo:  { label: "💼 Trabajo",   tareas: [] },
        estudios: { label: "📚 Estudios",  tareas: [] },
        personal: { label: "🏠 Personal",  tareas: [] }
    };

    // Distribuir cada tarea en su categoría correspondiente
    filtradas.forEach(t => {
        if (categorias[t.categoria]) {
            categorias[t.categoria].tareas.push(t);
        }
    });

    // Mostrar mensaje si no hay tareas que coincidan con los filtros
    if (filtradas.length === 0) {
        const vacio = document.createElement("li");
        vacio.classList.add("vacio");
        vacio.textContent = "No hay tareas aquí todavía 👀";
        lista.appendChild(vacio);
        actualizarContador(tareas);
        return;
    }

    // Renderizar cada grupo de categoría con sus tareas
    Object.entries(categorias).forEach(([key, grupo]) => {
        if (grupo.tareas.length === 0) return;

        // Encabezado de categoría
        const seccion = document.createElement("li");
        seccion.classList.add("categoria-header");
        seccion.textContent = grupo.label;
        lista.appendChild(seccion);

        // Tareas de esta categoría
        grupo.tareas.forEach(t => {
            const li = document.createElement("li");
            li.setAttribute("data-id", t.id);
            if (t.completada) li.classList.add("completada");

            // Formatear fecha de DD/MM/YYYY si existe
            let fechaTexto = "";
            if (t.fecha_limite) {
                const [year, month, day] = t.fecha_limite.split("-");
                fechaTexto = `<span class="fecha">📅 ${day}/${month}/${year}</span>`;
            }

            // Etiqueta de prioridad con color según nivel
            const etiquetas = { alta: "🔴 Alta", media: "🟡 Media", baja: "🟢 Baja" };
            const etiquetaPrioridad = `<span class="prioridad prioridad-${t.prioridad}">${etiquetas[t.prioridad]}</span>`;

            // Construir el HTML de cada tarea
            // Los botones de completar y editar solo aparecen si no está completada
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

    // Actualizar contador con el total real (sin filtros)
    actualizarContador(tareas);
}


// ── 4. Funciones de acciones (CRUD) ───────────────────────────

async function agregarTarea() {
    /*
     * Lee los valores del formulario y crea una nueva tarea
     * en el backend via POST. Si el título está vacío no hace nada.
     * Limpia el formulario y recarga las tareas al terminar.
     */
    const input = document.getElementById("nueva-tarea");
    const fecha = document.getElementById("fecha-limite");
    const prioridad = document.getElementById("prioridad");
    const categoria = document.getElementById("categoria");
    const titulo = input.value.trim();

    // No crear tarea si el título está vacío
    if (!titulo) return;

    try {
        await fetch("/tareas", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                titulo,
                fecha_limite: fecha.value || null,  // null si no hay fecha
                prioridad: prioridad.value,
                categoria: categoria.value
            })
        });

        // Limpiar formulario y volver a valores por defecto
        input.value = "";
        fecha.value = "";
        prioridad.value = "media";
        categoria.value = "personal";

        mostrarNotificacion("Tarea agregada", "exito");
        cargarTareas();
    } catch (error) {
        mostrarNotificacion("Error al agregar la tarea", "error");
    }
}

async function completar(id) {
    /*
     * Marca una tarea como completada via PUT.
     * El backend verifica que la tarea pertenezca al usuario actual.
     */
    try {
        await fetch(`/tareas/${id}`, { method: "PUT" });
        mostrarNotificacion("¡Tarea completada! ✓", "exito");
        cargarTareas();
    } catch (error) {
        mostrarNotificacion("Error al completar la tarea", "error");
    }
}

async function eliminar(id) {
    /*
     * Pide confirmación al usuario antes de eliminar la tarea.
     * Si confirma, envía DELETE al backend y recarga la lista.
     * El backend verifica que la tarea pertenezca al usuario actual.
     */

    // Pedir confirmación antes de eliminar — acción irreversible
    const confirmado = confirm("¿Estás seguro que deseas eliminar esta tarea?");
    if (!confirmado) return;

    try {
        const res = await fetch(`/tareas/${id}`, { method: "DELETE" });
        const data = await res.json();

        if (res.ok) {
            mostrarNotificacion(data.mensaje, "exito");
            cargarTareas();
        } else {
            mostrarNotificacion(data.error, "error");
        }
    } catch (error) {
        mostrarNotificacion("Error al eliminar la tarea", "error");
    }
}

async function editar(id, tituloActual) {
    /*
     * Convierte el título de una tarea en un input editable.
     * El botón "Editar" cambia a "Guardar" mientras se edita.
     * Se puede guardar haciendo click en "Guardar" o presionando Enter.
     * Envía PATCH al backend con el nuevo título.
     */
    const li = document.querySelector(`[data-id="${id}"]`);
    const spanTitulo = li.querySelector(".titulo");

    // Reemplazar el span del título por un input editable
    const input = document.createElement("input");
    input.type = "text";
    input.value = tituloActual;
    input.classList.add("input-editar");
    spanTitulo.replaceWith(input);
    input.focus();

    // Cambiar el botón editar a guardar
    const btnGuardar = li.querySelector(".btn-editar");
    btnGuardar.textContent = "💾 Guardar";
    btnGuardar.onclick = async () => {
        const nuevoTitulo = input.value.trim();
        if (!nuevoTitulo) return;

        try {
            await fetch(`/tareas/${id}`, {
                method: "PATCH",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ titulo: nuevoTitulo })
            });
            mostrarNotificacion("Tarea actualizada", "exito");
            cargarTareas();
        } catch (error) {
            mostrarNotificacion("Error al editar la tarea", "error");
        }
    };

    // Guardar también presionando Enter
    input.addEventListener("keypress", (e) => {
        if (e.key === "Enter") btnGuardar.click();
    });
}


// ── 5. Funciones de filtros, búsqueda y orden ─────────────────

function cambiarFiltro(filtro, btn) {
    /*
     * Actualiza el filtro activo y resalta el botón seleccionado.
     * No hace llamadas al backend — filtra desde tareasCache.
     */
    filtroActual = filtro;

    // Quitar clase activo de todos los botones y ponerla solo al seleccionado
    document.querySelectorAll(".btn-filtro").forEach(b => b.classList.remove("activo"));
    btn.classList.add("activo");

    renderizarTareas(tareasCache);
}

function buscar(texto) {
    /*
     * Actualiza el texto de búsqueda y re-renderiza la lista.
     * Se llama en cada tecla presionada (oninput en el HTML).
     * No hace llamadas al backend — filtra desde tareasCache.
     */
    textoBusqueda = texto.toLowerCase().trim();
    renderizarTareas(tareasCache);
}

function cambiarOrden(orden) {
    /*
     * Actualiza el criterio de ordenamiento y re-renderiza la lista.
     * Se llama cuando el usuario selecciona una opción del selector.
     * No hace llamadas al backend — ordena desde tareasCache.
     */
    ordenActual = orden;
    renderizarTareas(tareasCache);
}


// ── 6. Inicialización ──────────────────────────────────────────

document.addEventListener("DOMContentLoaded", () => {
    /*
     * Se ejecuta cuando el DOM está completamente cargado.
     * Carga las tareas iniciales y configura el evento Enter
     * en el input de nueva tarea.
     */

    // Cargar tareas al iniciar la página
    cargarTareas();

    // Permitir agregar tareas presionando Enter en el input principal
    document.getElementById("nueva-tarea").addEventListener("keypress", e => {
        if (e.key === "Enter") agregarTarea();
    });
});