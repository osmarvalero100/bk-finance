#!/usr/bin/env python3
"""
Script para ejecutar tests de la API de Finanzas Personales
"""

import subprocess
import sys
import os

def run_command(command, description):
    """Ejecutar comando y mostrar descripción"""
    print(f"\n{'='*60}")
    print(f"🚀 {description}")
    print(f"{'='*60}")

    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)

        if result.stdout:
            print("📋 Output:")
            print(result.stdout)

        if result.stderr:
            print("⚠️  Warnings/Errors:")
            print(result.stderr)

        if result.returncode == 0:
            print(f"✅ {description} completado exitosamente!")
        else:
            print(f"❌ Error en {description}")
            print(f"Código de salida: {result.returncode}")

        return result.returncode == 0

    except Exception as e:
        print(f"❌ Error ejecutando {description}: {e}")
        return False

def main():
    """Función principal"""
    print("🧪 Test Suite - API de Finanzas Personales")
    print("=" * 60)

    # Verificar que estamos en el ambiente virtual correcto
    if not hasattr(sys, 'real_prefix') and sys.base_prefix == sys.prefix:
        print("⚠️  Advertencia: No se detecta ambiente virtual activo")
        print("Es recomendable activar el ambiente virtual antes de ejecutar tests:")
        print("  . venv/bin/activate && python run_tests.py")
        print()

    # Cambiar al directorio del proyecto
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    success = True

    # 1. Verificar dependencias
    if not run_command("python -c 'import pytest, httpx, sqlalchemy' && echo 'Dependencies OK'",
                      "Verificando dependencias"):
        print("❌ No se pueden ejecutar tests sin las dependencias necesarias")
        return 1

    # 2. Ejecutar tests unitarios
    success &= run_command(
        ". venv/bin/activate && python -m pytest tests/unit/ -v",
        "Ejecutando tests unitarios"
    )

    # 3. Ejecutar tests de integración
    success &= run_command(
        ". venv/bin/activate && python -m pytest tests/integration/ -v",
        "Ejecutando tests de integración"
    )

    # 4. Ejecutar todos los tests con cobertura
    success &= run_command(
        ". venv/bin/activate && python -m pytest tests/ --cov=app --cov-report=html --cov-report=term",
        "Ejecutando todos los tests con reporte de cobertura"
    )

    # 5. Mostrar resumen
    print(f"\n{'='*60}")
    if success:
        print("🎉 ¡Todos los tests pasaron exitosamente!")
        print("📊 Reporte de cobertura generado en htmlcov/index.html")
    else:
        print("⚠️  Algunos tests fallaron. Revisa el output anterior.")
        return 1

    print(f"{'='*60}")
    print("💡 Para ejecutar tests específicos:")
    print("   python -m pytest tests/unit/test_expenses.py -v")
    print("   python -m pytest tests/integration/ -v")
    print("   python -m pytest -k 'test_create' -v")
    print(f"{'='*60}")

    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())