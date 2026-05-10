#!/usr/bin/env python3
"""
Script de pruebas automatizadas para el Sistema de Gestión de Tareas
Ejecuta una serie de tests para verificar el funcionamiento de la API
"""

import requests
import json
import time
import sys
from typing import Dict, Any

class TestAPI:
    def __init__(self, base_url: str = "http://localhost:5000"):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.session.headers.update({'Content-Type': 'application/json'})
        self.test_user = f"testuser_{int(time.time())}"  # Usuario único
        self.test_password = "test1234"
        self.tests_passed = 0
        self.tests_failed = 0
    
    def log_test(self, test_name: str, success: bool, message: str = ""):
        """Registra el resultado de un test"""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
        if message:
            print(f"    └─ {message}")
        
        if success:
            self.tests_passed += 1
        else:
            self.tests_failed += 1
    
    def test_server_status(self) -> bool:
        """Test 1: Verificar que el servidor esté disponible"""
        try:
            response = self.session.get(f"{self.base_url}/status")
            success = response.status_code == 200
            
            if success:
                data = response.json()
                message = f"Status: {data.get('status', 'Unknown')}, DB: {data.get('database', 'Unknown')}"
            else:
                message = f"HTTP {response.status_code}"
            
            self.log_test("Servidor disponible", success, message)
            return success
            
        except Exception as e:
            self.log_test("Servidor disponible", False, f"Error de conexión: {e}")
            return False
    
    def test_user_registration(self) -> bool:
        """Test 2: Registro de usuario exitoso"""
        data = {
            "usuario": self.test_user,
            "contraseña": self.test_password
        }
        
        try:
            response = self.session.post(f"{self.base_url}/registro", json=data)
            success = response.status_code == 201
            
            if success:
                result = response.json()
                message = f"Usuario '{result.get('usuario')}' registrado"
            else:
                error_data = response.json() if response.headers.get('content-type') == 'application/json' else {}
                message = f"HTTP {response.status_code}: {error_data.get('error', 'Error desconocido')}"
            
            self.log_test("Registro de usuario", success, message)
            return success
            
        except Exception as e:
            self.log_test("Registro de usuario", False, f"Error: {e}")
            return False
    
    def test_duplicate_registration(self) -> bool:
        """Test 3: Verificar que no se permitan usuarios duplicados"""
        data = {
            "usuario": self.test_user,
            "contraseña": "different_password"
        }
        
        try:
            response = self.session.post(f"{self.base_url}/registro", json=data)
            success = response.status_code == 409  # Esperamos conflict
            
            if success:
                message = "Duplicado correctamente rechazado"
            else:
                message = f"HTTP {response.status_code} (se esperaba 409)"
            
            self.log_test("Prevención de usuarios duplicados", success, message)
            return success
            
        except Exception as e:
            self.log_test("Prevención de usuarios duplicados", False, f"Error: {e}")
            return False
    
    def test_invalid_registration(self) -> bool:
        """Test 4: Verificar validación en registro"""
        invalid_cases = [
            ({"usuario": "ab", "contraseña": "1234"}, "Usuario muy corto"),
            ({"usuario": "validuser", "contraseña": "123"}, "Contraseña muy corta"),
            ({"usuario": "", "contraseña": "1234"}, "Usuario vacío"),
            ({"contraseña": "1234"}, "Campo usuario faltante"),
            ({"usuario": "validuser"}, "Campo contraseña faltante")
        ]
        
        all_passed = True
        
        for data, description in invalid_cases:
            try:
                response = self.session.post(f"{self.base_url}/registro", json=data)
                success = response.status_code == 400  # Esperamos bad request
                
                if not success:
                    all_passed = False
                    self.log_test(f"Validación: {description}", False, f"HTTP {response.status_code} (se esperaba 400)")
                
            except Exception as e:
                all_passed = False
                self.log_test(f"Validación: {description}", False, f"Error: {e}")
        
        if all_passed:
            self.log_test("Validaciones de registro", True, "Todas las validaciones correctas")
        
        return all_passed
    
    def test_login_success(self) -> bool:
        """Test 5: Login exitoso"""
        data = {
            "usuario": self.test_user,
            "contraseña": self.test_password
        }
        
        try:
            response = self.session.post(f"{self.base_url}/login", json=data)
            success = response.status_code == 200
            
            if success:
                result = response.json()
                message = f"Login exitoso para '{result.get('usuario')}'"
            else:
                error_data = response.json() if response.headers.get('content-type') == 'application/json' else {}
                message = f"HTTP {response.status_code}: {error_data.get('error', 'Error desconocido')}"
            
            self.log_test("Login exitoso", success, message)
            return success
            
        except Exception as e:
            self.log_test("Login exitoso", False, f"Error: {e}")
            return False
    
    def test_login_invalid_credentials(self) -> bool:
        """Test 6: Login con credenciales incorrectas"""
        invalid_cases = [
            ({"usuario": self.test_user, "contraseña": "wrongpass"}, 401, "Contraseña incorrecta"),
            ({"usuario": "nonexistentuser", "contraseña": self.test_password}, 404, "Usuario inexistente"),
            ({"usuario": self.test_user}, 400, "Campo contraseña faltante"),
            ({"contraseña": self.test_password}, 400, "Campo usuario faltante")
        ]
        
        all_passed = True
        
        for data, expected_status, description in invalid_cases:
            try:
                response = self.session.post(f"{self.base_url}/login", json=data)
                success = response.status_code == expected_status
                
                if success:
                    self.log_test(f"Login inválido: {description}", True, f"Correctamente rechazado (HTTP {expected_status})")
                else:
                    all_passed = False
                    self.log_test(f"Login inválido: {description}", False, f"HTTP {response.status_code} (se esperaba {expected_status})")
                
            except Exception as e:
                all_passed = False
                self.log_test(f"Login inválido: {description}", False, f"Error: {e}")
        
        return all_passed
    
    def test_protected_endpoint_without_auth(self) -> bool:
        """Test 7: GET /tareas es publico (HTML)"""
        new_session = requests.Session()

        try:
            response = new_session.get(f"{self.base_url}/tareas")
            success = response.status_code == 200
            if success:
                ok_html = "text/html" in (response.headers.get("content-type") or "").lower()
                message = "HTML recibido" if ok_html else "200 pero sin content-type html claro"
                success = success and ok_html
            else:
                message = f"HTTP {response.status_code} (se esperaba 200)"

            self.log_test("GET /tareas sin autenticacion", success, message)
            return success

        except Exception as e:
            self.log_test("GET /tareas sin autenticacion", False, f"Error: {e}")
            return False
    
    def test_protected_endpoint_with_auth(self) -> bool:
        """Test 8: GET /tareas con sesion iniciada"""
        try:
            response = self.session.get(f"{self.base_url}/tareas")
            success = response.status_code == 200

            if success:
                message = "Pagina accesible con sesion"
            else:
                message = f"HTTP {response.status_code}"

            self.log_test("GET /tareas con autenticacion", success, message)
            return success

        except Exception as e:
            self.log_test("GET /tareas con autenticacion", False, f"Error: {e}")
            return False
    
    def test_logout(self) -> bool:
        """Test 9: Logout de usuario"""
        try:
            response = self.session.post(f"{self.base_url}/logout")
            success = response.status_code == 200
            
            if success:
                result = response.json()
                message = f"Logout exitoso: {result.get('mensaje', 'OK')}"
            else:
                message = f"HTTP {response.status_code}"
            
            self.log_test("Logout de usuario", success, message)
            return success
            
        except Exception as e:
            self.log_test("Logout de usuario", False, f"Error: {e}")
            return False
    
    def test_access_after_logout(self) -> bool:
        """Test 10: Tras logout /tareas sigue siendo publico"""
        try:
            response = self.session.get(f"{self.base_url}/tareas")
            success = response.status_code == 200

            if success:
                message = "Pagina publica accesible tras logout"
            else:
                message = f"HTTP {response.status_code} (se esperaba 200)"

            self.log_test("GET /tareas despues de logout", success, message)
            return success

        except Exception as e:
            self.log_test("GET /tareas despues de logout", False, f"Error: {e}")
            return False
    
    def run_all_tests(self):
        """Ejecuta todos los tests"""
        print("🧪 INICIANDO TESTS AUTOMATIZADOS")
        print("=" * 50)
        
        # Lista de tests a ejecutar
        tests = [
            self.test_server_status,
            self.test_user_registration,
            self.test_duplicate_registration,
            self.test_invalid_registration,
            self.test_login_success,
            self.test_login_invalid_credentials,
            self.test_protected_endpoint_without_auth,
            self.test_protected_endpoint_with_auth,
            self.test_logout,
            self.test_access_after_logout
        ]
        
        # Ejecutar tests
        for i, test in enumerate(tests, 1):
            print(f"\n[{i:2d}/10] ", end="")
            test()
            time.sleep(0.5)  # Pequeña pausa entre tests
        
        # Resumen final
        print("\n" + "=" * 50)
        print("📊 RESUMEN DE TESTS")
        print("=" * 50)
        print(f"✅ Tests pasados: {self.tests_passed}")
        print(f"❌ Tests fallidos: {self.tests_failed}")
        print(f"📊 Total tests: {self.tests_passed + self.tests_failed}")
        
        success_rate = (self.tests_passed / (self.tests_passed + self.tests_failed)) * 100
        print(f"🎯 Tasa de éxito: {success_rate:.1f}%")
        
        if self.tests_failed == 0:
            print("\n🎉 ¡TODOS LOS TESTS PASARON!")
            print("✨ El sistema está funcionando correctamente")
            return True
        else:
            print(f"\n⚠️  {self.tests_failed} test(s) fallaron")
            print("🔧 Revisar los errores antes de continuar")
            return False

def main():
    """Función principal"""
    print("🚀 Sistema de Gestión de Tareas - Test Suite")
    print("Verificando API en http://localhost:5000")
    print("=" * 50)
    
    tester = TestAPI()
    
    # Verificar conexión inicial
    if not tester.test_server_status():
        print("\n❌ No se puede conectar al servidor")
        print("💡 Asegúrate de que el servidor esté ejecutándose:")
        print("   python servidor.py")
        sys.exit(1)
    
    # Ejecutar todos los tests
    success = tester.run_all_tests()
    
    # Código de salida
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()