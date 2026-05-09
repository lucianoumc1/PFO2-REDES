#!/usr/bin/env python3
"""Rellena el sistema con usuarios de prueba y un par de comprobaciones."""

import json
import time

import requests


class DataSetup:
    def __init__(self, base_url: str = "http://localhost:5000"):
        self.base_url = base_url.rstrip("/")
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})

    def check_server(self) -> bool:
        try:
            r = self.session.get(f"{self.base_url}/status")
            return r.status_code == 200
        except Exception:
            return False

    def show_system_status(self):
        print("\nEstado del sistema")
        print("=" * 35)
        try:
            response = self.session.get(f"{self.base_url}/status")
            if response.status_code == 200:
                data = response.json()
                print(f"Estado: {data.get('status', '?')}")
                print(f"Base de datos: {data.get('database', '?')}")
                print(f"Usuarios: {data.get('usuarios_registrados', 0)}")
                print(f"Tareas: {data.get('tareas_totales', 0)}")
                print(f"Version: {data.get('version', '?')}")
                print(f"Hora: {data.get('timestamp', '?')}")
            else:
                print(f"No pude leer /status (HTTP {response.status_code}).")
        except Exception as e:
            print(f"Error: {e}")

    def create_demo_users(self):
        demo_users = [
            {"usuario": "admin", "contraseña": "admin123"},
            {"usuario": "user1", "contraseña": "user123"},
            {"usuario": "testuser", "contraseña": "test123"},
            {"usuario": "demo", "contraseña": "demo123"},
            {"usuario": "guest", "contraseña": "guest123"},
        ]

        print("Creando usuarios de demo...")
        print("-" * 40)
        created = []

        for user_data in demo_users:
            try:
                response = self.session.post(
                    f"{self.base_url}/registro", json=user_data
                )
                if response.status_code == 201:
                    print(f"  Listo: {user_data['usuario']}")
                    created.append(user_data["usuario"])
                elif response.status_code == 409:
                    print(f"  Ya existia: {user_data['usuario']}")
                else:
                    err = response.json().get("error", "?")
                    print(f"  Fallo {user_data['usuario']}: {err}")
            except Exception as e:
                print(f"  Error con {user_data['usuario']}: {e}")

        print(f"\nUsuarios nuevos en esta pasada: {len(created)}")
        return created

    def test_user_logins(self, usernames):
        print("\nProbando logins...")
        print("-" * 35)

        test_cases = [
            {"usuario": "admin", "contraseña": "admin123"},
            {"usuario": "user1", "contraseña": "user123"},
            {"usuario": "demo", "contraseña": "demo123"},
        ]
        ok_count = 0

        for user_data in test_cases:
            try:
                response = self.session.post(f"{self.base_url}/login", json=user_data)
                if response.status_code == 200:
                    print(f"  Login ok: {user_data['usuario']}")
                    ok_count += 1
                    tareas_r = self.session.get(f"{self.base_url}/tareas")
                    if tareas_r.status_code == 200:
                        print("     /tareas responde 200")
                    else:
                        print(f"     /tareas -> HTTP {tareas_r.status_code}")
                    self.session.post(f"{self.base_url}/logout")
                else:
                    err = response.json().get("error", "?")
                    print(f"  Login mal: {user_data['usuario']} ({err})")
            except Exception as e:
                print(f"  Excepcion en {user_data['usuario']}: {e}")

        print(f"\nLogins bien: {ok_count}/{len(test_cases)}")
        return ok_count

    def generate_demo_scenarios(self):
        print("\nEscenarios de demo")
        print("=" * 45)

        scenarios = [
            {
                "name": "Registro exitoso",
                "user": {
                    "usuario": f"scenario_user_{int(time.time())}",
                    "contraseña": "demo123",
                },
                "description": "Usuario nuevo",
            },
            {
                "name": "Login despues de registro",
                "user": {"usuario": "admin", "contraseña": "admin123"},
                "description": "Usuario que ya esta",
            },
            {
                "name": "Acceso a tareas autenticado",
                "user": {"usuario": "admin", "contraseña": "admin123"},
                "description": "Ruta protegida",
            },
        ]

        for i, scenario in enumerate(scenarios, 1):
            print(f"\n[{i}] {scenario['name']}")
            print(f"    {scenario['description']}")
            print("-" * 30)

            if scenario["name"] == "Registro exitoso":
                r = self.session.post(
                    f"{self.base_url}/registro", json=scenario["user"]
                )
                print("  registro ok" if r.status_code == 201 else f"  HTTP {r.status_code}")

            elif scenario["name"] == "Login despues de registro":
                r = self.session.post(f"{self.base_url}/login", json=scenario["user"])
                print("  login ok" if r.status_code == 200 else f"  HTTP {r.status_code}")

            elif scenario["name"] == "Acceso a tareas autenticado":
                lr = self.session.post(f"{self.base_url}/login", json=scenario["user"])
                if lr.status_code == 200:
                    tr = self.session.get(f"{self.base_url}/tareas")
                    print(
                        "  tareas ok"
                        if tr.status_code == 200
                        else f"  tareas HTTP {tr.status_code}"
                    )
                else:
                    print(f"  login previo HTTP {lr.status_code}")

            time.sleep(0.5)

    def create_documentation_examples(self):
        print("\nEjemplos para api_examples.json")
        print("=" * 45)
        examples = []
        user_data = {"usuario": "doc_example", "contraseña": "example123"}

        print("\n[1] POST /registro")
        try:
            response = self.session.post(
                f"{self.base_url}/registro", json=user_data
            )
            examples.append(
                {
                    "endpoint": "POST /registro",
                    "request": user_data,
                    "status_code": response.status_code,
                    "response": response.json()
                    if response.status_code in (200, 201, 400, 409)
                    else {"error": "servidor"},
                }
            )
            print(f"  codigo {response.status_code}")
        except Exception as e:
            print(f"  error: {e}")

        print("\n[2] POST /login")
        try:
            response = self.session.post(f"{self.base_url}/login", json=user_data)
            examples.append(
                {
                    "endpoint": "POST /login",
                    "request": user_data,
                    "status_code": response.status_code,
                    "response": response.json()
                    if response.status_code in (200, 400, 401, 404)
                    else {"error": "servidor"},
                }
            )
            print(f"  codigo {response.status_code}")
        except Exception as e:
            print(f"  error: {e}")

        print("\n[3] GET /tareas")
        try:
            response = self.session.get(f"{self.base_url}/tareas")
            examples.append(
                {
                    "endpoint": "GET /tareas",
                    "request": "N/A (sesion)",
                    "status_code": response.status_code,
                    "response": "HTML"
                    if response.status_code == 200
                    else response.json(),
                }
            )
            print(f"  codigo {response.status_code}")
        except Exception as e:
            print(f"  error: {e}")

        try:
            with open("api_examples.json", "w", encoding="utf-8") as f:
                json.dump(examples, f, indent=2, ensure_ascii=False)
            print("\nGuardado en api_examples.json")
        except Exception as e:
            print(f"No pude guardar el json: {e}")

        return examples

    def run_complete_setup(self):
        print("Setup de datos de prueba")
        print("=" * 55)

        if not self.check_server():
            print("No hay servidor en http://localhost:5000")
            print("Arranca antes: python servidor.py")
            return False

        print("Servidor respondiendo.")

        creados = self.create_demo_users()
        self.test_user_logins(creados)
        self.generate_demo_scenarios()
        self.create_documentation_examples()
        self.show_system_status()

        print("\n" + "=" * 55)
        print("Fin del setup.")
        print("=" * 55)
        return True


def main():
    print("Sistema de tareas - setup de datos")
    print("Rellena usuarios demo y genera ejemplos.")
    print("=" * 55)
    DataSetup().run_complete_setup()


if __name__ == "__main__":
    main()
