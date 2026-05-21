# views.py

from flask_appbuilder.views import ModelView
from flask_appbuilder.models.sqla.interface import SQLAInterface
from flask_appbuilder import BaseView, expose
from sqlalchemy import func
from datetime import date
from collections import Counter
from .models import Cliente, Servicio, Tecnico, OrdenServicio
from . import appbuilder, db
from .ia_servicio import analizar_ventas


# =========================================================
# CRUD CLIENTES
# =========================================================

class ClienteView(ModelView):
    datamodel = SQLAInterface(Cliente)

    list_columns = [
        "nombre",
        "telefono",
        "correo",
        "direccion"
    ]


# =========================================================
# CRUD SERVICIOS
# =========================================================

class ServicioView(ModelView):
    datamodel = SQLAInterface(Servicio)

    list_columns = [
        "nombre",
        "descripcion",
        "precio"
    ]


# =========================================================
# CRUD TECNICOS
# =========================================================

class TecnicoView(ModelView):
    datamodel = SQLAInterface(Tecnico)

    list_columns = [
        "nombre",
        "especialidad",
        "telefono"
    ]


# =========================================================
# CRUD ORDENES
# =========================================================

class OrdenServicioView(ModelView):
    datamodel = SQLAInterface(OrdenServicio)

    list_columns = [
        "fecha",
        "estado",
        "costo",
        "cliente",
        "servicio",
        "tecnico"
    ]

    add_columns = [
        "cliente",
        "servicio",
        "tecnico",
        "fecha",
        "estado",
        "costo"
    ]

    edit_columns = [
        "cliente",
        "servicio",
        "tecnico",
        "fecha",
        "estado",
        "costo"
    ]

    def pre_add(self, item):

        if item.servicio:
            item.costo = item.servicio.precio

        if item.fecha and item.fecha >= date.today():
            item.estado = "Activo"
        else:
            item.estado = "Inactivo"

    def pre_update(self, item):

        if item.servicio:
            item.costo = item.servicio.precio

        if item.fecha and item.fecha >= date.today():
            item.estado = "Activo"
        else:
            item.estado = "Inactivo"


# =========================================================
# REGISTRO CRUDS
# =========================================================

appbuilder.add_view(
    ClienteView,
    "Clientes",
    icon="fa-user",
    category="Gestión"
)

appbuilder.add_view(
    ServicioView,
    "Servicios",
    icon="fa-tools",
    category="Gestión"
)

appbuilder.add_view(
    TecnicoView,
    "Técnicos",
    icon="fa-wrench",
    category="Gestión"
)

appbuilder.add_view(
    OrdenServicioView,
    "Órdenes",
    icon="fa-clipboard",
    category="Gestión"
)


# =========================================================
# DASHBOARD IA
# =========================================================

class DashboardView(BaseView):

    default_view = "index"
    route_base = "/dashboard"

    @expose("/")
    def index(self):

        # =====================================================
        # METRICAS GENERALES
        # =====================================================

        total_clientes = db.session.query(
            func.count(Cliente.id)
        ).scalar()

        total_ordenes = db.session.query(
            func.count(OrdenServicio.id)
        ).scalar()

        ingresos = db.session.query(
            func.sum(OrdenServicio.costo)
        ).scalar()

        # =====================================================
        # SERVICIOS MAS SOLICITADOS
        # =====================================================

        servicios = db.session.query(
            Servicio.nombre,
            func.count(OrdenServicio.id)
        ).join(
            OrdenServicio
        ).group_by(
            Servicio.nombre
        ).all()

        labels = [s[0] for s in servicios]
        valores = [s[1] for s in servicios]

        # ==========================================
        # PREDICCIÓN INTELIGENTE
        # ==========================================

        servicios_historicos = db.session.query(
            Servicio.nombre
        ).join(
            OrdenServicio
        ).all()

        lista_servicios = [s[0] for s in servicios_historicos]

        conteo_servicios = Counter(lista_servicios)

        servicio_prediccion = max(
            conteo_servicios,
            key=conteo_servicios.get
        )

        cantidad_prediccion = conteo_servicios[servicio_prediccion]

        # Generar predicción automática
        if cantidad_prediccion >= 6:
            nivel_demanda = "ALTA"
            recomendacion_prediccion = (
                f"Se recomienda aumentar recursos "
                f"para el servicio '{servicio_prediccion}' "
                f"debido a su alta demanda."
            )

        elif cantidad_prediccion >= 4:
            nivel_demanda = "MEDIA"
            recomendacion_prediccion = (
                f"El servicio '{servicio_prediccion}' "
                f"mantiene una demanda constante."
            )

        else:
            nivel_demanda = "BAJA"
            recomendacion_prediccion = (
                f"El servicio '{servicio_prediccion}' "
                f"presenta baja demanda."
            )

        # =====================================================
        # SERVICIO MAS SOLICITADO
        # =====================================================

        servicio_top = db.session.query(
            Servicio.nombre,
            func.count(OrdenServicio.id).label("total")
        ).join(
            OrdenServicio
        ).group_by(
            Servicio.nombre
        ).order_by(
            func.count(OrdenServicio.id).desc()
        ).first()

        # =====================================================
        # TECNICO MAS ACTIVO
        # =====================================================

        tecnico_top = db.session.query(
            Tecnico.nombre,
            func.count(OrdenServicio.id).label("total")
        ).join(
            OrdenServicio
        ).group_by(
            Tecnico.nombre
        ).order_by(
            func.count(OrdenServicio.id).desc()
        ).first()

        # =====================================================
        # TENDENCIA MENSUAL
        # =====================================================

        ventas_mes = db.session.query(
            func.month(OrdenServicio.fecha),
            func.sum(OrdenServicio.costo)
        ).group_by(
            func.month(OrdenServicio.fecha)
        ).all()

        meses = [f"Mes {v[0]}" for v in ventas_mes]
        totales_mes = [float(v[1]) for v in ventas_mes]

        # =====================================================
        # DATOS COMPLETOS PARA IA
        # =====================================================

        ordenes_detalle = db.session.query(
            OrdenServicio.id,
            OrdenServicio.fecha,
            OrdenServicio.estado,
            OrdenServicio.costo,
            Cliente.nombre,
            Servicio.nombre,
            Tecnico.nombre
        ).join(
            Cliente
        ).join(
            Servicio
        ).join(
            Tecnico
        ).all()

        # =====================================================
        # FORMATEAR DATOS PARA IA
        # =====================================================

        datos_ia = []

        for orden in ordenes_detalle:

            datos_ia.append({
                "id": orden[0],
                "fecha": str(orden[1]),
                "estado": orden[2],
                "costo": float(orden[3]),
                "cliente": orden[4],
                "servicio": orden[5],
                "tecnico": orden[6]
            })

        # =====================================================
        # RESUMEN INTELIGENTE
        # =====================================================

        servicios_top = db.session.query(
            Servicio.nombre,
            func.count(OrdenServicio.id)
        ).join(
            OrdenServicio
        ).group_by(
            Servicio.nombre
        ).order_by(
            func.count(OrdenServicio.id).desc()
        ).limit(5).all()

        tecnicos_top = db.session.query(
            Tecnico.nombre,
            func.count(OrdenServicio.id)
        ).join(
            OrdenServicio
        ).group_by(
            Tecnico.nombre
        ).order_by(
            func.count(OrdenServicio.id).desc()
        ).limit(5).all()

        estados = db.session.query(
            OrdenServicio.estado,
            func.count(OrdenServicio.id)
        ).group_by(
            OrdenServicio.estado
        ).all()

        resumen_negocio = f"""
                RESUMEN GENERAL DEL NEGOCIO

                CLIENTES REGISTRADOS:
                {total_clientes}

                ORDENES TOTALES:
                {total_ordenes}

                INGRESOS TOTALES:
                Bs. {ingresos}

                SERVICIOS MAS SOLICITADOS:
                {servicios_top}

                TECNICOS MAS ACTIVOS:
                {tecnicos_top}

                ESTADOS DE LAS ORDENES:
                {estados}

                DETALLE COMPLETO DE ORDENES:
                {datos_ia}
                """

        # =====================================================
        # ANALISIS IA
        # =====================================================

        try:
            analisis_venta = analizar_ventas(resumen_negocio)
            # =========================================
            # PREDICCIONES INTELIGENTES
            # =========================================

            predicciones = []

            # Servicio más rentable
            if servicio_top:
                predicciones.append(
                    f"El servicio '{servicio_top[0]}' continuará siendo uno de los más solicitados el próximo mes."
                )

            # Técnico sobrecargado
            if tecnico_top:
                predicciones.append(
                    f"El técnico '{tecnico_top[0]}' presenta alta carga operativa y podría requerir apoyo adicional."
                )

            # Ingresos altos
            if ingresos and ingresos > 10000:
                predicciones.append(
                    "Los ingresos muestran una tendencia positiva y estable."
                )

            # Órdenes pendientes
            ordenes_pendientes = db.session.query(
                func.count(OrdenServicio.id)
            ).filter(
                OrdenServicio.estado == "Pendiente"
            ).scalar()

            if ordenes_pendientes > 10:
                predicciones.append(
                    "Existe riesgo de retrasos debido al alto número de órdenes pendientes."
                )

            # Recomendaciones automáticas
            recomendaciones_ia = [
                "Promocionar servicios premium para incrementar ingresos.",
                "Redistribuir órdenes entre técnicos.",
                "Reducir tiempos de atención.",
                "Aplicar mantenimiento preventivo a clientes frecuentes.",
            ]
        except Exception as e:

            print("ERROR IA:", e)

            analisis_venta = """
            ❌ No se pudo generar el análisis inteligente.
            Verifica la API o la conexión.
            """
        clientes_frecuentes = db.session.query(
            Cliente.nombre,
            func.count(OrdenServicio.id).label("total")
        ).join(
            OrdenServicio
        ).group_by(
            Cliente.nombre
        ).order_by(
            func.count(OrdenServicio.id).desc()
        ).limit(5).all()

        clientes_labels = [c[0] for c in clientes_frecuentes]
        clientes_valores = [c[1] for c in clientes_frecuentes]  

        tecnicos_activos = db.session.query(
            Tecnico.nombre,
            func.count(OrdenServicio.id)
        ).join(
            OrdenServicio
        ).group_by(
            Tecnico.nombre
        ).order_by(
            func.count(OrdenServicio.id).desc()
        ).limit(5).all()

        tecnicos_labels = [t[0] for t in tecnicos_activos]
        tecnicos_valores = [t[1] for t in tecnicos_activos] 

        ventas_mes = db.session.query(
            func.month(OrdenServicio.fecha),
            func.sum(OrdenServicio.costo)
        ).group_by(
            func.month(OrdenServicio.fecha)
        ).all()

        meses = [f"Mes {m[0]}" for m in ventas_mes]
        totales_mes = [float(m[1]) for m in ventas_mes]
        # =====================================================
        # RENDER TEMPLATE
        # =====================================================

        return self.render_template(
            "dashboard/dashboard.html",

            total_clientes=total_clientes,
            total_ordenes=total_ordenes,
            ingresos=ingresos,

            labels=labels,
            valores=valores,

            servicio_top=servicio_top,
            tecnico_top=tecnico_top,

            meses=meses,
            totales_mes=totales_mes,

            analisis_venta=analisis_venta,
            clientes_labels=clientes_labels,
            clientes_valores=clientes_valores,

            tecnicos_labels=tecnicos_labels,
            tecnicos_valores=tecnicos_valores,

            predicciones=predicciones,
            recomendaciones_ia=recomendaciones_ia,
            ordenes_pendientes=ordenes_pendientes,

            servicio_prediccion=servicio_prediccion,
            cantidad_prediccion=cantidad_prediccion,
            nivel_demanda=nivel_demanda,
            recomendacion_prediccion=recomendacion_prediccion

        )


# =========================================================
# REGISTRO DASHBOARD
# =========================================================

appbuilder.add_view(
    DashboardView,
    "Dashboard",
    icon="fa-chart-bar",
    category="Reportes"
)