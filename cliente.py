#!/usr/bin/env python3
"""Cliente de consola para probar la API del sistema de tareas."""

import sys

import requests


class ClienteTareas:
    def __init__(self, base_url: str = "http://localhost:5000"):
        self.base_url = base_url.rstrip("/")
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})

    def probar_servidor(self) -> bool:
        try:
            r = self.session.get(f"{self.base_url}/status")
            return r.status_code == 200
        except Exception:
            return False

    def mostrar_menu(self):
        """Aqui van emojis y titulos tipo menu; el resto de mensajes va sin eso."""
        print("\n" + "=" * 50)
        print("🚀 SISTEMA DE GESTIÓN DE TAREAS - CLIENTE")
        print("=" * 50)
        print("1. 📝 Registrar nuevo usuario")
        print("2. 🔐 Iniciar sesión")
        print("3. 📋 Ver página de tareas")
        print("4. 📊 Ver estado del sistema")
        print("5. 🚪 Cerrar sesión")
        print("6. ❌ Salir")
        print("=" * 50)

    def registrar_usuario(self):
        print("\nRegistro de usuario")
        print("-" * 30)

        usuario = input("Usuario (min. 3 caracteres): ").strip()
        if len(usuario) < 3:
            print("El usuario debe tener al menos 3 caracteres.")
            return

        contraseña = input("Contraseña (min. 4 caracteres): ").strip()
        if len(contraseña) < 4:
            print("La contraseña debe tener al menos 4 caracteres.")
            return

        data = {"usuario": usuario, "contraseña": contraseña}

        try:
            response = self.session.post(f"{self.base_url}/registro", json=data)
            if response.status_code == 201:
                result = response.json()
                print(result.get("mensaje", "Ok"))
                print(f"Usuario: {result['usuario']}")
                print(f"Fecha: {result['fecha_registro']}")
            else:
                err = response.json().get("error", "Error desconocido")
                print(f"Error: {err}")
        except requests.exceptions.ConnectionError:
            print("No se puede conectar al servidor. ¿Esta en marcha?")
        except Exception as e:
            print(f"Algo salio mal: {e}")

    def iniciar_sesion(self):
        print("\nInicio de sesion")
        print("-" * 25)

        usuario = input("Usuario: ").strip()
        contraseña = input("Contraseña: ").strip()
        data = {"usuario": usuario, "contraseña": contraseña}

        try:
            response = self.session.post(f"{self.base_url}/login", json=data)
            if response.status_code == 200:
                result = response.json()
                print(result.get("mensaje", "Ok"))
                print(f"Usuario: {result['usuario']}")
                print(f"Sesion: {result['sesion_iniciada']}")
            else:
                err = response.json().get("error", "Error desconocido")
                print(f"Error: {err}")
        except requests.exceptions.ConnectionError:
            print("No se puede conectar al servidor.")
        except Exception as e:
            print(f"Algo salio mal: {e}")

    def ver_tareas(self):
        print("\nAbriendo tareas...")

        try:
            response = self.session.get(f"{self.base_url}/tareas")
            if response.status_code == 200:
                print("Listo. La pagina respondio bien.")
                print(f"En el navegador: {self.base_url.rstrip('/')}/tareas")
            elif response.status_code == 401:
                err = response.json().get("error", "No autenticado")
                print(f"Autenticacion: {err}")
                print("Prueba a iniciar sesion antes.")
            else:
                print(f"Respuesta HTTP {response.status_code}")
        except requests.exceptions.ConnectionError:
            print("No se puede conectar al servidor.")
        except Exception as e:
            print(f"Algo salio mal: {e}")

    def ver_estado(self):
        print("\nEstado del sistema")
        print("-" * 25)

        try:
            response = self.session.get(f"{self.base_url}/status")
            if response.status_code == 200:
                result = response.json()
                print(f"Estado: {result['status']}")
                print(f"Base de datos: {result['database']}")
                print(f"Usuarios: {result['usuarios_registrados']}")
                print(f"Tareas: {result['tareas_totales']}")
                print(f"Hora: {result['timestamp']}")
                print(f"Version: {result['version']}")
            else:
                print(f"No pude leer el estado (HTTP {response.status_code}).")
        except requests.exceptions.ConnectionError:
            print("No se puede conectar al servidor.")
        except Exception as e:
            print(f"Algo salio mal: {e}")

    def cerrar_sesion(self):
        print("\nCerrando sesion...")

        try:
            response = self.session.post(f"{self.base_url}/logout")
            if response.status_code == 200:
                result = response.json()
                print(result.get("mensaje", "Ok"))
                print(f"Logout: {result['fecha_logout']}")
            else:
                print("No se pudo cerrar la sesion.")
        except requests.exceptions.ConnectionError:
            print("No se puede conectar al servidor.")
        except Exception as e:
            print(f"Algo salio mal: {e}")

    def ejecutar(self):
        print("Arrancando cliente...")

        if not self.probar_servidor():
            print("No hay servidor en http://localhost:5000")
            print("Levantalo con: python servidor.py")
            sys.exit(1)

        print("Conexion ok.")

        while True:
            try:
                self.mostrar_menu()
                opcion = input("\nOpcion (1-6): ").strip()

                if opcion == "1":
                    self.registrar_usuario()
                elif opcion == "2":
                    self.iniciar_sesion()
                elif opcion == "3":
                    self.ver_tareas()
                elif opcion == "4":
                    self.ver_estado()
                elif opcion == "5":
                    self.cerrar_sesion()
                elif opcion == "6":
                    print("\nHasta luego.")
                    break
                else:
                    print("Opcion no valida. Elige del 1 al 6.")

                input("\nEnter para seguir...")

            except KeyboardInterrupt:
                print("\n\nSaliendo.")
                break
            except Exception as e:
                print(f"Algo salio mal: {e}")
                input("Enter para seguir...")


def main():
    ClienteTareas().ejecutar()


if __name__ == "__main__":
    main()
