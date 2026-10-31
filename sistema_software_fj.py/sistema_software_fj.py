import logging
from abc import ABC, abstractmethod

logging.basicConfig(filename='eventos_y_errores.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class ErrorSistema(Exception): pass
class DatoInvalidoError(ErrorSistema): pass
class ReservaInvalidaError(ErrorSistema): pass
class ServicioNoDisponibleError(ErrorSistema): pass

class Entidad(ABC):
    @abstractmethod
    def mostrar_informacion(self): pass

class Cliente(Entidad):
    def __init__(self, nombre, identificacion, correo):
        self.__nombre = None; self.__identificacion = None; self.__correo = None
        self.nombre = nombre; self.identificacion = identificacion; self.correo = correo

    @property
    def nombre(self): return self.__nombre
    @nombre.setter
    def nombre(self, valor):
        if not isinstance(valor, str) or not valor.strip(): raise DatoInvalidoError("El nombre no puede estar vacío.")
        self.__nombre = valor.strip()

    @property
    def identificacion(self): return self.__identificacion
    @identificacion.setter
    def identificacion(self, valor):
        if not isinstance(valor, str) or len(valor) < 5: raise DatoInvalidoError("La identificacion debe tener al menos 5 caracteres.")
        self.__identificacion = valor

    @property
    def correo(self): return self.__correo
    @correo.setter
    def correo(self, valor):
        if not isinstance(valor, str) or "@" not in valor or "." not in valor: raise DatoInvalidoError(f"El correo '{valor}' no es valido.")
        self.__correo = valor

    def mostrar_informacion(self): return f"Cliente: {self.__nombre} | ID: {self.__identificacion}"

class Servicio(ABC):
    def __init__(self, nombre, costo_base):
        self.nombre = nombre; self.costo_base = costo_base; self.disponible = True
    @abstractmethod
    def describir(self): pass
    @abstractmethod
    def calcular_costo(self, duracion, descuento=0.0, impuesto=0.0): pass

class ReservaSala(Servicio):
    def describir(self): return f"Sala '{self.nombre}'."
    def calcular_costo(self, duracion, descuento=0.0, impuesto=0.0): return (self.costo_base * duracion) * (1 - descuento) * (1 + impuesto)

class AlquilerEquipo(Servicio):
    def describir(self): return f"Equipo '{self.nombre}'."
    def calcular_costo(self, duracion, descuento=0.0, impuesto=0.0): return (self.costo_base * duracion) * (1 - descuento) * (1 + impuesto)

class AsesoriaEspecializada(Servicio):
    def describir(self): return f"Asesoria '{self.nombre}'."
    def calcular_costo(self, duracion, descuento=0.0, impuesto=0.0): return (self.costo_base * max(1, duracion)) * (1 - descuento) * (1 + impuesto)

class Reserva:
    def __init__(self, cliente, servicio, duracion):
        self.cliente = cliente; self.servicio = servicio; self.duracion = duracion; self._estado = "PENDIENTE"

    def confirmar(self, descuento=0.0, impuesto=0.0):
        print(f"  Procesando reserva para {self.cliente.nombre}...")
        try:
            if self._estado == "CANCELADA": raise ReservaInvalidaError("No se puede confirmar una reserva cancelada.")
            if self.duracion <= 0: raise ValueError("Duracion invalida.")
            if not self.servicio.disponible: raise ServicioNoDisponibleError("El servicio solicitado no esta disponible.")
        except ValueError as e:
            logging.error(f"Error de valor: {e}")
            raise ReservaInvalidaError("Fallo en los datos de la reserva") from e
        except (ReservaInvalidaError, ServicioNoDisponibleError) as e:
            logging.error(f"Error en reserva: {e}")
            print(f"  [RECHAZADA] {e}")
        else:
            self._estado = "CONFIRMADA"
            costo = self.servicio.calcular_costo(self.duracion, descuento, impuesto)
            logging.info(f"Reserva exitosa para {self.cliente.nombre}.")
            print(f"  CONFIRMADA. Costo total: ${costo:,.2f}")
        finally:
            print("  -> Intento finalizado.")

    def cancelar(self):
        if self._estado == "CONFIRMADA":
            self._estado = "CANCELADA"
            print(f"  Reserva de {self.cliente.nombre} CANCELADA.")

if __name__ == "__main__":
    print("=== SISTEMA INTEGRAL SOFTWARE FJ ===")
    
    print("\n[Operacion 1] Cliente valido:")
    try:
        c1 = Cliente("Brayan Gallego", "12345", "brayan@correo.com")
        print("  Exito:", c1.mostrar_informacion())
        logging.info("Operacion 1 exitosa.")
    except Exception as e: print("  Error:", e)

    print("\n[Operacion 2] Cliente invalido (correo malo):")
    try: c2 = Cliente("Carlos", "67890", "correo-sin-arroba")
    except Exception as e:
        print("  Error:", e); logging.error(f"Operacion 2 fallida: {e}")

    print("\n[Operacion 3] Servicios y Polimorfismo (Lista):")
    sala = ReservaSala("Sala VIP", 50000); equipo = AlquilerEquipo("Proyector", 30000); asesoria = AsesoriaEspecializada("Clase Python", 100000)
    for s in [sala, equipo, asesoria]:
        print(f"  {s.describir()} - Costo base: ${s.calcular_costo(1):,.2f}")
        logging.info(f"Servicio creado: {s.describir()}")

    print("\n[Operacion 4] Reserva exitosa:")
    r1 = Reserva(c1, sala, 2); r1.confirmar()

    print("\n[Operacion 5] Reserva fallida (duracion negativa):")
    c3 = Cliente("Ana", "55555", "ana@correo.com"); r2 = Reserva(c3, equipo, -3)
    try: r2.confirmar()
    except Exception as e: print("  Error encadenado:", e)

    print("\n[Operacion 6] Reserva fallida (servicio no disponible):")
    asesoria.disponible = False; r3 = Reserva(c3, asesoria, 1); r3.confirmar()

    print("\n[Operacion 7] Reserva fallida (cancelada):")
    r1.cancelar(); r1.confirmar()

    print("\n[Operacion 8] Calculo con impuestos:")
    print(f"  Costo: ${asesoria.calcular_costo(2, descuento=0.10, impuesto=0.19):,.2f}"); logging.info("Operacion 8 exitosa.")

    print("\n[Operacion 9] Cliente invalido (ID corto):")
    try: c4 = Cliente("Pedro", "123", "pedro@correo.com")
    except Exception as e:
        print("  Error:", e); logging.error(f"Operacion 9 fallida: {e}")

    print("\n[Operacion 10] Fin de la simulacion.")
    logging.info("Operacion 10: Fin.")