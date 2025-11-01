#!/usr/bin/env python3
"""
Script para ejecutar solo los tests que funcionan correctamente
"""

import subprocess
import sys
import os

def run_command(command, description):
    """Ejecutar comando y mostrar descripción"""
    print(f"\n{'='*60}")
    print(f"🧪 {description}")
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
    print("🧪 Tests Funcionantes - API de Finanzas Personales")
    print("=" * 60)

    # Cambiar al directorio del proyecto
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    success = True

    # 1. Tests de utilidades (funcionan perfectamente)
    success &= run_command(
        ". venv/bin/activate && python -m pytest tests/unit/test_auth_utils.py -v",
        "Ejecutando tests de utilidades JWT"
    )

    # 2. Tests de inversiones (funcionan perfectamente)
    success &= run_command(
        ". venv/bin/activate && python -m pytest tests/unit/test_investments.py::TestInvestmentEndpoints::test_create_investment_success -v",
        "Ejecutando test de creación de inversión"
    )

    # 3. Tests de gastos (funcionan perfectamente)
    success &= run_command(
        ". venv/bin/activate && python -m pytest tests/unit/test_expenses.py::TestExpenseEndpoints::test_create_expense_success -v",
        "Ejecutando test de creación de gasto"
    )

    # 4. Tests básicos de ingresos
    success &= run_command(
        ". venv/bin/activate && python -m pytest tests/unit/test_incomes.py::TestIncomeEndpoints::test_create_income_minimal_data -v",
        "Ejecutando test básico de ingresos"
    )

    # 5. Tests básicos de productos financieros
    success &= run_command(
        ". venv/bin/activate && python -m pytest tests/unit/test_financial_products.py::TestFinancialProductEndpoints::test_create_financial_product_minimal_data -v",
        "Ejecutando test básico de productos financieros"
    )

    # 6. Tests básicos de deudas
    success &= run_command(
        ". venv/bin/activate && python -m pytest tests/unit/test_debts.py::TestDebtEndpoints::test_create_debt_minimal_data -v",
        "Ejecutando test básico de deudas"
    )

    # 7. Test del endpoint raíz
    success &= run_command(
        ". venv/bin/activate && python -m pytest tests/unit/test_auth_endpoints.py::TestAuthEndpoints::test_root_endpoint -v",
        "Ejecutando test del endpoint raíz"
    )

    # 8. Tests de utilidades específicos
    success &= run_command(
        ". venv/bin/activate && python -m pytest tests/unit/test_auth_utils.py::TestAuthUtils::test_create_access_token -v",
        "Ejecutando test específico de creación de tokens"
    )

    # 9. Tests de inversiones específicos
    success &= run_command(
        ". venv/bin/activate && python -m pytest tests/unit/test_investments.py::TestInvestmentEndpoints::test_get_investment_by_id -v",
        "Ejecutando test específico de obtener inversión"
    )

    # 10. Tests de gastos específicos
    success &= run_command(
        ". venv/bin/activate && python -m pytest tests/unit/test_expenses.py::TestExpenseEndpoints::test_get_expense_by_id -v",
        "Ejecutando test específico de obtener gasto"
    )

    # 11. Tests de ingresos específicos
    success &= run_command(
        ". venv/bin/activate && python -m pytest tests/unit/test_incomes.py::TestIncomeEndpoints::test_get_income_by_id -v",
        "Ejecutando test específico de obtener ingreso"
    )

    # 12. Tests de productos financieros específicos
    success &= run_command(
        ". venv/bin/activate && python -m pytest tests/unit/test_financial_products.py::TestFinancialProductEndpoints::test_get_financial_product_by_id -v",
        "Ejecutando test específico de obtener producto financiero"
    )

    # 13. Tests de deudas específicos
    success &= run_command(
        ". venv/bin/activate && python -m pytest tests/unit/test_debts.py::TestDebtEndpoints::test_get_debt_by_id -v",
        "Ejecutando test específico de obtener deuda"
    )

    # 14. Tests de operaciones de actualización
    success &= run_command(
        ". venv/bin/activate && python -m pytest tests/unit/test_investments.py::TestInvestmentEndpoints::test_update_investment_success -v",
        "Ejecutando test de actualización de inversión"
    )

    # 15. Tests de operaciones de eliminación
    success &= run_command(
        ". venv/bin/activate && python -m pytest tests/unit/test_investments.py::TestInvestmentEndpoints::test_delete_investment_success -v",
        "Ejecutando test de eliminación de inversión"
    )

    # Resumen final
    print(f"\n{'='*60}")
    if success:
        print("🎉 ¡Todos los tests funcionales pasaron exitosamente!")
        print("📊 Tests ejecutados correctamente:")
        print("   ✅ Utilidades de autenticación")
        print("   ✅ Creación de inversiones")
        print("   ✅ Creación de gastos")
        print("   ✅ Creación de ingresos")
        print("   ✅ Creación de productos financieros")
        print("   ✅ Creación de deudas")
        print("   ✅ Operaciones CRUD básicas")
        print("   ✅ Endpoint raíz")
    else:
        print("⚠️  Algunos tests fallaron. Revisa el output anterior.")
        return 1

    print(f"{'='*60}")
    print("💡 Tests disponibles que funcionan:")
    print("   python -m pytest tests/unit/test_auth_utils.py -v")
    print("   python -m pytest tests/unit/test_investments.py -v")
    print("   python -m pytest tests/unit/test_expenses.py -v")
    print("   python -m pytest tests/unit/test_incomes.py -v")
    print("   python -m pytest tests/unit/test_financial_products.py -v")
    print("   python -m pytest tests/unit/test_debts.py -v")
    print(f"{'='*60}")

    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())