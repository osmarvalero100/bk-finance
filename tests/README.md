# Tests - API de Finanzas Personales

Este directorio contiene la suite completa de tests para la API de Finanzas Personales.

## 📁 Estructura de Tests

```
tests/
├── conftest.py                    # Configuración y fixtures globales
├── README.md                      # Esta documentación
├── unit/                          # Tests unitarios
│   ├── test_auth_utils.py         # Tests de utilidades de autenticación
│   ├── test_auth_endpoints.py     # Tests de endpoints de autenticación
│   ├── test_expenses.py           # Tests de endpoints de gastos
│   ├── test_incomes.py            # Tests de endpoints de ingresos
│   ├── test_investments.py        # Tests de endpoints de inversiones
│   ├── test_financial_products.py # Tests de endpoints de productos financieros
│   └── test_debts.py              # Tests de endpoints de deudas
├── integration/                   # Tests de integración
│   └── test_full_flows.py         # Tests de flujos completos
└── fixtures/                      # Fixtures adicionales (vacío por ahora)
```

## 🚀 Ejecución de Tests

### Ejecutar todos los tests

```bash
# Usando el script personalizado
python run_tests.py

# Usando pytest directamente
python -m pytest tests/ -v

# Con cobertura
python -m pytest tests/ --cov=app --cov-report=html
```

### Ejecutar tests específicos

```bash
# Tests unitarios de gastos
python -m pytest tests/unit/test_expenses.py -v

# Tests de integración
python -m pytest tests/integration/ -v

# Tests que contienen "create" en el nombre
python -m pytest -k "test_create" -v

# Tests marcados como unitarios
python -m pytest -m "unit" -v
```

### Ejecutar tests con diferentes niveles de verbosidad

```bash
# Solo resultados
python -m pytest tests/ -q

# Resultados detallados
python -m pytest tests/ -v

# Muy detallado (incluye prints)
python -m pytest tests/ -vv -s
```

## 🧪 Tipos de Tests

### Tests Unitarios
- **Ubicación**: `tests/unit/`
- **Propósito**: Probar funciones individuales y métodos aislados
- **Ejemplos**:
  - Utilidades de autenticación (hash, tokens)
  - Validación de datos individuales
  - Lógica de negocio específica

### Tests de Integración
- **Ubicación**: `tests/integration/`
- **Propósito**: Probar interacción entre múltiples componentes
- **Ejemplos**:
  - Flujos completos de usuario
  - Interacción entre diferentes endpoints
  - Consistencia de datos

## 🔧 Configuración

### Archivo `conftest.py`
Contiene fixtures globales utilizadas en múltiples tests:

- `db_session`: Sesión de base de datos de prueba
- `test_user`: Usuario de prueba autenticado
- `auth_headers`: Headers de autenticación para requests
- `test_expense`, `test_income`, etc.: Datos de prueba para cada entidad
- `async_client`: Cliente HTTP para tests async

### Archivo `pytest.ini`
Configuración global de pytest:

- Rutas de búsqueda de tests
- Opciones por defecto
- Marcadores personalizados

## 📋 Cobertura de Tests

### Tests de Autenticación
- ✅ Registro de usuarios (éxito y errores)
- ✅ Login/logout
- ✅ Validación de tokens JWT
- ✅ Manejo de errores de autenticación
- ✅ Información de usuario actual

### Tests de Gastos
- ✅ CRUD completo (Crear, Leer, Actualizar, Eliminar)
- ✅ Validación de datos
- ✅ Filtros por categoría
- ✅ Paginación
- ✅ Resumen por categoría
- ✅ Manejo de errores

### Tests de Ingresos
- ✅ CRUD completo
- ✅ Validación de datos
- ✅ Filtros por fuente
- ✅ Paginación
- ✅ Resumen por fuente
- ✅ Manejo de errores

### Tests de Inversiones
- ✅ CRUD completo
- ✅ Validación de datos
- ✅ Filtros por tipo
- ✅ Cálculo de rendimiento
- ✅ Resumen por tipo
- ✅ Manejo de errores

### Tests de Productos Financieros
- ✅ CRUD completo
- ✅ Diferentes tipos (cuentas, tarjetas, préstamos)
- ✅ Balance consolidado
- ✅ Resumen por tipo
- ✅ Manejo de errores

### Tests de Deudas
- ✅ CRUD completo
- ✅ Marcar como pagadas
- ✅ Balance total de deudas
- ✅ Resumen por tipo
- ✅ Manejo de errores

### Tests de Integración
- ✅ Flujos completos de usuario
- ✅ Aislamiento de datos entre usuarios
- ✅ Consistencia de datos
- ✅ Paginación en todas las entidades
- ✅ Operaciones concurrentes

## 🎯 Mejores Prácticas

### Escritura de Tests
1. **Nombres descriptivos**: `test_create_expense_success`
2. **Arrange-Act-Assert**: Estructura clara en cada test
3. **Fixtures reutilizables**: Usar conftest.py para datos compartidos
4. **Asserts específicos**: Verificar exactamente lo que se espera
5. **Mensajes de error claros**: Facilitar debugging

### Organización
1. **Separación por funcionalidad**: Un archivo por módulo
2. **Tests independientes**: Cada test debe poder correr solo
3. **Limpieza automática**: Usar fixtures para limpiar datos
4. **Documentación**: Comentar tests complejos

### Ejecución
1. **CI/CD**: Integrar en pipeline de desarrollo
2. **Coverage mínimo**: Mantener cobertura > 80%
3. **Tests rápidos**: Optimizar para ejecución rápida
4. **Paralelización**: Usar pytest-xdist para tests en paralelo

## 🔍 Debugging de Tests

### Comandos útiles

```bash
# Ejecutar test específico con debugging
python -m pytest tests/unit/test_expenses.py::TestExpenseEndpoints::test_create_expense_success -v -s

# Ver variables durante ejecución
python -m pytest tests/ -v -s --pdb

# Generar reporte de cobertura detallado
python -m pytest tests/ --cov=app --cov-report=html --cov-report=term-missing
```

### Problemas comunes

1. **Base de datos**: Asegurar limpieza entre tests
2. **Async tests**: Usar `pytest.mark.asyncio` correctamente
3. **Fixtures**: Verificar dependencias entre fixtures
4. **Tiempo**: Usar timeouts apropiados para tests lentos

## 📊 Métricas de Calidad

### Cobertura esperada
- **Líneas de código**: > 85%
- **Ramas**: > 80%
- **Funciones**: > 90%

### Tiempo de ejecución
- **Tests unitarios**: < 30 segundos
- **Tests de integración**: < 2 minutos
- **Tests completos**: < 5 minutos

## 🚀 Próximas mejoras

- [ ] Tests de carga y performance
- [ ] Tests de seguridad avanzados
- [ ] Tests de API externa (si aplica)
- [ ] Mocks para dependencias externas
- [ ] Tests de contratos (pact)
- [ ] Tests de mutación