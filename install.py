#!/usr/bin/env python3
"""Instala dependencias y deja listo el entorno del proyecto."""

import os
import platform
import subprocess
import sys
import venv


class ProjectInstaller:
    def __init__(self):
        self.project_name = "Sistema de Gestion de Tareas"
        self.python_version = (
            f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
        )
        self.os_info = platform.system()
        self.venv_name = "venv"

    def get_python_path(self):
        if self.os_info == "Windows":
            return os.path.join(self.venv_name, "Scripts", "python")
        return os.path.join(self.venv_name, "bin", "python")

    def get_pip_path(self):
        if self.os_info == "Windows":
            return os.path.join(self.venv_name, "Scripts", "pip")
        return os.path.join(self.venv_name, "bin", "pip")

    def print_header(self):
        print("=" * 60)
        print(f"Instalador - {self.project_name}")
        print("=" * 60)
        print(f"Python: {self.python_version}")
        print(f"Sistema: {self.os_info}")
        print(f"Carpeta: {os.getcwd()}")
        print("=" * 60)

    def check_python_version(self):
        print("\nComprobando version de Python...")
        if sys.version_info < (3, 7):
            print(f"Esta version ({self.python_version}) no sirve; hace falta 3.7 o mas.")
            return False
        print(f"Version ok ({self.python_version}).")
        return True

    def create_virtual_environment(self):
        print(f"\nCreando entorno virtual '{self.venv_name}'...")

        if os.path.exists(self.venv_name):
            print(f"Ya existe '{self.venv_name}'.")
            response = input("¿Quieres borrarlo y crearlo de nuevo? (y/n): ").lower().strip()
            if response == "y":
                import shutil

                shutil.rmtree(self.venv_name)
                print("He borrado el entorno anterior.")
            else:
                print("Sigo con el que ya hay.")
                return True

        try:
            venv.create(self.venv_name, with_pip=True)
            print(f"Entorno '{self.venv_name}' creado.")
            return True
        except Exception as e:
            print(f"No pude crear el venv: {e}")
            return False

    def install_requirements(self):
        print("\nInstalando dependencias...")
        pip_path = self.get_pip_path()

        if not os.path.exists("requirements.txt"):
            print("No hay requirements.txt; escribo uno basico.")
            basic = [
                "Flask==2.3.3",
                "bcrypt==4.0.1",
                "Werkzeug==2.3.7",
                "requests==2.31.0",
            ]
            with open("requirements.txt", "w") as f:
                f.write("\n".join(basic))
            print("Listo, archivo creado.")

        try:
            subprocess.run(
                [pip_path, "install", "--upgrade", "pip"],
                check=True,
                capture_output=True,
                text=True,
            )
            print("pip actualizado.")

            subprocess.run(
                [pip_path, "install", "-r", "requirements.txt"],
                check=True,
                capture_output=True,
                text=True,
            )
            print("Paquetes instalados.")

            listed = subprocess.run(
                [pip_path, "list"],
                check=True,
                capture_output=True,
                text=True,
            )
            needles = ("flask", "bcrypt", "werkzeug", "requests")
            lines = [
                ln
                for ln in listed.stdout.split("\n")
                if any(n in ln.lower() for n in needles)
            ]
            if lines:
                print("\nAlgunos paquetes relevantes:")
                for ln in lines:
                    if ln.strip():
                        print(f"   {ln.strip()}")
            return True

        except subprocess.CalledProcessError as e:
            print(f"Fallo al instalar: {e}")
            print("STDOUT:", e.stdout)
            print("STDERR:", e.stderr)
            return False

    def verify_installation(self):
        print("\nComprobando que los imports funcionen...")
        python_path = self.get_python_path()
        test_script = """
import sys
try:
    import flask
    print("flask ok", getattr(flask, "__version__", "?"))
except ImportError as e:
    print("flask fallo:", e)
try:
    import bcrypt
    print("bcrypt ok")
except ImportError as e:
    print("bcrypt fallo:", e)
try:
    import sqlite3
    print("sqlite3 ok")
except ImportError as e:
    print("sqlite3 fallo:", e)
try:
    import requests
    print("requests ok")
except ImportError as e:
    print("requests fallo:", e)
"""
        try:
            result = subprocess.run(
                [python_path, "-c", test_script],
                check=True,
                capture_output=True,
                text=True,
            )
            print("Salida:")
            for line in result.stdout.split("\n"):
                if line.strip():
                    print(f"   {line}")
            return True
        except subprocess.CalledProcessError as e:
            print(f"La verificacion fallo: {e}")
            return False

    def create_run_scripts(self):
        print("\nGenerando scripts de arranque...")
        py = self.get_python_path()

        if self.os_info == "Windows":
            with open("run_server.bat", "w") as f:
                f.write(f'@echo off\necho Servidor...\n"{py}" servidor.py\npause\n')
            with open("run_client.bat", "w") as f:
                f.write(f'@echo off\necho Cliente...\n"{py}" cliente.py\npause\n')
            with open("run_tests.bat", "w") as f:
                f.write(f'@echo off\necho Tests...\n"{py}" test_api.py\npause\n')
            print("Creados run_server.bat, run_client.bat, run_tests.bat.")
        else:
            with open("run_server.sh", "w") as f:
                f.write(f'#!/bin/bash\necho "Servidor..."\n"{py}" servidor.py\n')
            with open("run_client.sh", "w") as f:
                f.write(f'#!/bin/bash\necho "Cliente..."\n"{py}" cliente.py\n')
            with open("run_tests.sh", "w") as f:
                f.write(f'#!/bin/bash\necho "Tests..."\n"{py}" test_api.py\n')
            os.chmod("run_server.sh", 0o755)
            os.chmod("run_client.sh", 0o755)
            os.chmod("run_tests.sh", 0o755)
            print("Creados los .sh con permiso de ejecucion.")

    def show_activation_instructions(self):
        print("\nActivar el entorno virtual")
        print("-" * 40)
        if self.os_info == "Windows":
            print(f"  CMD:        {self.venv_name}\\Scripts\\activate.bat")
            print(f"  PowerShell: {self.venv_name}\\Scripts\\Activate.ps1")
        else:
            print(f"  bash/zsh:   source {self.venv_name}/bin/activate")
        print("  Para salir: deactivate")

    def show_usage_instructions(self):
        print("\nComo arrancar el proyecto")
        print("-" * 30)
        print("1) Activa el venv (arriba).")
        print("2) Servidor: python servidor.py")
        if self.os_info == "Windows":
            print("   (o doble clic en run_server.bat)")
        else:
            print("   (o ./run_server.sh)")
        print("3) Navegador: http://localhost:5000")
        print("4) Cliente consola: python cliente.py")
        if self.os_info == "Windows":
            print("   (o run_client.bat)")
        else:
            print("   (o ./run_client.sh)")
        print("5) Tests: python test_api.py")

    def install(self):
        self.print_header()
        if not self.check_python_version():
            return False
        if not self.create_virtual_environment():
            return False
        if not self.install_requirements():
            return False
        if not self.verify_installation():
            return False

        self.create_run_scripts()
        self.show_activation_instructions()
        self.show_usage_instructions()

        print("\n" + "=" * 60)
        print("Instalacion terminada.")
        print("=" * 60)
        print("venv listo, dependencias instaladas, scripts creados.")
        return True


def main():
    installer = ProjectInstaller()
    try:
        ok = installer.install()
        sys.exit(0 if ok else 1)
    except KeyboardInterrupt:
        print("\n\nInstalacion cancelada.")
        sys.exit(1)
    except Exception as e:
        print(f"\nError: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
