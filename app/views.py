from flask_appbuilder.views import ModelView
from flask_appbuilder.models.sqla.interface import SQLAInterface
from .models import Cliente, Servicio, Tecnico, OrdenServicio
from . import appbuilder, db
from flask import render_template
from flask_appbuilder import BaseView, expose
from sqlalchemy import func

class ClienteView(ModelView):
    datamodel = SQLAInterface(Cliente)

    list_columns = [
        "nombre",
        "telefono",
        "correo",
        "direccion"
    ]
class ServicioView(ModelView):
    datamodel = SQLAInterface(Servicio)

    list_columns = [
        "nombre",
        "descripcion",
        "precio"
    ]
class TecnicoView(ModelView):
    datamodel = SQLAInterface(Tecnico)

    list_columns = [
        "nombre",
        "especialidad",
        "telefono"
    ]
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
class DashboardView(BaseView):

    default_view = "index"
    route_base = "/dashboard"

    @expose("/")
    def index(self):

        total_clientes = db.session.query(
            func.count(Cliente.id)
        ).scalar()

        total_ordenes = db.session.query(
            func.count(OrdenServicio.id)
        ).scalar()

        ingresos = db.session.query(
            func.sum(OrdenServicio.costo)
        ).scalar()

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

        return self.render_template(
            "dashboard/dashboard.html",
            total_clientes=total_clientes,
            total_ordenes=total_ordenes,
            ingresos=ingresos,
            labels=labels,
            valores=valores
        )

appbuilder.add_view(
    DashboardView,
    "Dashboard",
    icon="fa-chart-bar",
    category="Reportes"
)