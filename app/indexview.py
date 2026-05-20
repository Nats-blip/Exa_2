# app/indexview.py
from flask_appbuilder import IndexView
from flask_appbuilder.models.sqla.interface import SQLAInterface
from flask import flash
from sqlalchemy import func
from app.extensions import db
from app.models import Cliente, OrdenServicio, Servicio, Tecnico

class ServiTechIndexView(IndexView):
    index_template = 'servitech_index.html'
    
    def before_request(self):
        try:
            # Obtener estadísticas
            total_clientes = db.session.query(Cliente).count()
            total_tecnicos = db.session.query(Tecnico).count()
            total_servicios = db.session.query(Servicio).count()
            total_ordenes = db.session.query(OrdenServicio).count()
            
            # Calcular ingresos totales (suma de costos de órdenes finalizadas)
            ingresos = db.session.query(func.sum(OrdenServicio.costo)).filter(
                OrdenServicio.estado == 'Finalizado'
            ).scalar() or 0
            
            # Órdenes por estado
            pendientes = db.session.query(OrdenServicio).filter(
                OrdenServicio.estado == 'Pendiente'
            ).count()
            
            en_proceso = db.session.query(OrdenServicio).filter(
                OrdenServicio.estado == 'En proceso'
            ).count()
            
            finalizados = db.session.query(OrdenServicio).filter(
                OrdenServicio.estado == 'Finalizado'
            ).count()
            
            # Servicios más solicitados (para gráfica)
            servicios_populares = db.session.query(
                Servicio.nombre,
                func.count(OrdenServicio.id).label('total')
            ).join(OrdenServicio).group_by(Servicio.id).order_by(
                func.count(OrdenServicio.id).desc()
            ).limit(5).all()
            
            self.extra_args = {
                'total_clientes': total_clientes,
                'total_tecnicos': total_tecnicos,
                'total_servicios': total_servicios,
                'total_ordenes': total_ordenes,
                'ingresos_totales': ingresos,
                'ordenes_pendientes': pendientes,
                'ordenes_proceso': en_proceso,
                'ordenes_finalizadas': finalizados,
                'servicios_populares': servicios_populares
            }
        except Exception as e:
            # Si hay error, mostrar valores por defecto
            flash(f'Error al cargar estadísticas: {str(e)}', 'danger')
            self.extra_args = {
                'total_clientes': 0,
                'total_tecnicos': 0,
                'total_servicios': 0,
                'total_ordenes': 0,
                'ingresos_totales': 0,
                'ordenes_pendientes': 0,
                'ordenes_proceso': 0,
                'ordenes_finalizadas': 0,
                'servicios_populares': []
            }