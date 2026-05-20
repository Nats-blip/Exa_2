// static/js/custom.js
console.log('ServiTech Manager - Sistema de Gestión Técnica');

// Puedes añadir funcionalidades globales aquí
// Por ejemplo, confirmaciones para acciones peligrosas
document.addEventListener('DOMContentLoaded', function() {
    // Añadir confirmación a botones de eliminar
    const deleteButtons = document.querySelectorAll('.btn-delete');
    deleteButtons.forEach(btn => {
        btn.addEventListener('click', function(e) {
            if(!confirm('¿Estás seguro de que deseas eliminar este registro?')) {
                e.preventDefault();
            }
        });
    });
});