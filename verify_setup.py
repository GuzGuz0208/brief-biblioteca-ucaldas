#!/usr/bin/env python
"""
Script de verificación: valida que proyecto-v2 esté completamente inicializado.
Ejecutar con: python verify_setup.py
"""

import sys
import os
from pathlib import Path

def verify_structure():
    """Verifica la estructura de carpetas."""
    print("🔍 Verificando estructura...")

    base_path = Path("proyecto-v2")
    required_dirs = [
        "app",
        "app/core",
        "app/models",
        "app/repositories",
        "app/services",
        "app/api",
        "app/api/v1",
        "app/api/v1/endpoints",
        "app/tests",
    ]

    for dir_path in required_dirs:
        full_path = base_path / dir_path
        if not full_path.exists():
            print(f"❌ Falta carpeta: {full_path}")
            return False
        print(f"✅ {full_path}")

    return True


def verify_files():
    """Verifica que existan los archivos necesarios."""
    print("\n🔍 Verificando archivos...")

    base_path = Path("proyecto-v2")
    required_files = [
        # Root
        "requirements.txt",
        "README.md",

        # App
        "app/__init__.py",
        "app/main.py",

        # Core
        "app/core/config.py",

        # Models
        "app/models/__init__.py",
        "app/models/libro.py",
        "app/models/ejemplar.py",
        "app/models/estudiante.py",
        "app/models/prestamo.py",
        "app/models/multa.py",
        "app/models/reserva.py",

        # Repositories
        "app/repositories/__init__.py",
        "app/repositories/base.py",
        "app/repositories/memory.py",

        # Services
        "app/services/__init__.py",
        "app/services/biblioteca_service.py",

        # API
        "app/api/__init__.py",
        "app/api/v1/__init__.py",
        "app/api/v1/router.py",
        "app/api/v1/endpoints/__init__.py",

        # Tests
        "app/tests/__init__.py",
        "app/tests/conftest.py",
        "app/tests/test_libros.py",
        "app/tests/test_prestamos.py",
    ]

    all_exist = True
    for file_path in required_files:
        full_path = base_path / file_path
        if not full_path.exists():
            print(f"❌ Falta archivo: {full_path}")
            all_exist = False
        else:
            print(f"✅ {full_path}")

    return all_exist


def verify_imports():
    """Verifica que los módulos puedan importarse."""
    print("\n🔍 Verificando imports...")

    try:
        sys.path.insert(0, str(Path("proyecto-v2")))

        from app.models.libro import Libro
        print("✅ Models importables")

        from app.repositories.memory import MemoryRepository
        print("✅ Repositories importables")

        from app.services.biblioteca_service import BibliotecaService
        print("✅ Services importables")

        from app.main import app
        print("✅ FastAPI app importable")

        return True
    except Exception as e:
        print(f"❌ Error de import: {e}")
        return False


def verify_dependencies():
    """Verifica que las dependencias estén instaladas."""
    print("\n🔍 Verificando dependencias...")

    required = [
        "fastapi",
        "uvicorn",
        "pydantic",
        "pytest",
    ]

    all_installed = True
    for package in required:
        try:
            __import__(package)
            print(f"✅ {package} instalado")
        except ImportError:
            print(f"❌ {package} NO instalado")
            all_installed = False

    return all_installed


def main():
    """Ejecuta todas las verificaciones."""
    print("=" * 60)
    print("🔧 VERIFICACIÓN DE PROYECTO-V2")
    print("=" * 60)

    os.chdir(Path(__file__).parent)

    results = {
        "Estructura": verify_structure(),
        "Archivos": verify_files(),
        "Imports": verify_imports(),
        "Dependencias": verify_dependencies(),
    }

    print("\n" + "=" * 60)
    print("📊 RESULTADOS FINALES")
    print("=" * 60)

    for check, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{check:.<40} {status}")

    all_pass = all(results.values())

    print("\n" + "=" * 60)
    if all_pass:
        print("✨ PROYECTO-V2 ESTÁ COMPLETAMENTE INICIALIZADO")
        print("=" * 60)
        print("\n🚀 Para ejecutar el servidor:")
        print("   cd proyecto-v2")
        print("   uvicorn app.main:app --reload")
        print("\n🧪 Para ejecutar los tests:")
        print("   cd proyecto-v2")
        print("   pytest app/tests/ -v")
        return 0
    else:
        print("⚠️  HAY PROBLEMAS CON LA INICIALIZACIÓN")
        print("=" * 60)
        return 1


if __name__ == "__main__":
    sys.exit(main())
