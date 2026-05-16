from flask_appbuilder import Model
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy import Float 
from sqlalchemy import Date

class Cliente(Model):
    __tablename__ = 'clientes'
    id = Column(Integer, primary_key=True)
    nombre = Column(String(100), nullable=False)
    telefono = Column(String(20))
    correo = Column(String(100))
    direccion = Column(String(200))
    ordenes = relationship("OrdenServicio", back_populates="cliente")
    def __repr__(self):
        return self.nombre

class Servicio(Model):
    __tablename__ = 'servicios'
    id = Column(Integer, primary_key=True)
    nombre = Column(String(100), nullable=False)
    descripcion = Column(String(200))
    precio = Column(Float)
    ordenes = relationship("OrdenServicio", back_populates="servicio")

    def __repr__(self):
        return self.nombre

class Tecnico(Model):
    __tablename__ = 'tecnicos'
    id = Column(Integer, primary_key=True)
    nombre = Column(String(100), nullable=False)
    especialidad = Column(String(100))
    telefono = Column(String(20))
    ordenes = relationship("OrdenServicio", back_populates="tecnico")

    def __repr__(self):
        return self.nombre

class OrdenServicio(Model):
    __tablename__ = 'ordenes_servicio'
    id = Column(Integer, primary_key=True)
    fecha = Column(Date)
    estado = Column(String(50))
    costo = Column(Float)
    cliente_id = Column(Integer, ForeignKey("clientes.id"))
    servicio_id = Column(Integer, ForeignKey("servicios.id"))
    tecnico_id = Column(Integer, ForeignKey("tecnicos.id"))

    cliente = relationship("Cliente", back_populates="ordenes")
    servicio = relationship("Servicio", back_populates="ordenes")
    tecnico = relationship("Tecnico", back_populates="ordenes")

    def __repr__(self):
        return f"Orden {self.id}"