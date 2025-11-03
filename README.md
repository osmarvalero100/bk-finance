# API de Finanzas Personales

Una API REST completa para gestión de finanzas personales desarrollada con FastAPI y MySQL.

## Características

- ✅ Gestión completa de gastos, ingresos, inversiones, productos financieros y deudas
- ✅ Sistema de autenticación JWT seguro
- ✅ Documentación automática con Swagger/OpenAPI
- ✅ Base de datos MySQL con SQLAlchemy ORM
- ✅ Validación de datos con Pydantic
- ✅ Arquitectura escalable y mantenible
- ✅ CORS habilitado para desarrollo
- ✅ **Categorías personalizables** con colores, íconos y jerarquía
- ✅ **Métodos de pago personalizables**
- ✅ **Etiquetas flexibles** para organizar transacciones
- ✅ **API de presupuestos** para planificación financiera

## Tecnologías

- **Backend**: FastAPI (Python)
- **Base de datos**: MySQL
- **ORM**: SQLAlchemy
- **Autenticación**: JWT tokens
- **Validación**: Pydantic
- **Documentación**: Swagger/OpenAPI

## Instalación

### 1. Clonar el repositorio

```bash
git clone <url-del-repositorio>
cd bk-finance
```

### 2. Crear entorno virtual

```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\\Scripts\\activate
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4. Configurar variables de entorno

1. Copiar el archivo de ejemplo de variables de entorno:

```bash
cp .env.example .env
```

2. Editar el archivo `.env` con tus configuraciones específicas:

```bash
nano .env  # o tu editor preferido
```

#### Variables de entorno disponibles:

| Variable | Descripción | Valor por defecto | Requerido |
|----------|-------------|-------------------|-----------|
| `DATABASE_URL` | URL de conexión a la base de datos | `mysql+pymysql://username:password@localhost/finance_db` | ✅ |
| `SECRET_KEY` | Clave secreta para JWT (cambiar en producción) | `your-super-secret-key-change-this-in-production` | ✅ |
| `ALGORITHM` | Algoritmo de encriptación JWT | `HS256` | ❌ |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Minutos de expiración del token | `30` | ❌ |
| `API_HOST` | Host del servidor API | `localhost` | ❌ |
| `API_PORT` | Puerto del servidor API | `8000` | ❌ |
| `DEBUG` | Modo debug (desarrollo/producción) | `True` | ❌ |
| `BACKEND_CORS_ORIGINS` | Orígenes permitidos para CORS | `["http://localhost:3000", "http://localhost:8080"]` | ❌ |

#### Configuración de base de datos:

La variable `DATABASE_URL` soporta diferentes motores de base de datos:

- **MySQL**: `mysql+pymysql://usuario:contraseña@host:puerto/nombre_db`
- **PostgreSQL**: `postgresql://usuario:contraseña@host:puerto/nombre_db`
- **SQLite**: `sqlite:///./nombre_db.db`

**Ejemplo para MySQL:**
```env
DATABASE_URL=mysql+pymysql://root:mipassword@localhost:3306/finance_db
```

**Ejemplo para desarrollo con SQLite:**
```env
DATABASE_URL=sqlite:///./finance_dev.db
```

### 5. Ejecutar migraciones

```bash
python -c "from app.core.database import engine, Base; Base.metadata.create_all(bind=engine)"
```

### 6. Iniciar servidor

```bash
uvicorn app.main:app --reload
```

La API estará disponible en `http://localhost:8000`

## Documentación de la API

Una vez iniciado el servidor, la documentación interactiva estará disponible en:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Uso básico

### 1. Registro de usuario

```bash
curl -X POST "http://localhost:8000/auth/register" \
     -H "Content-Type: application/json" \
     -d '{
       "email": "usuario@example.com",
       "username": "usuario123",
       "password": "contraseña123",
       "full_name": "Nombre Completo"
     }'
```

### 2. Inicio de sesión

```bash
curl -X POST "http://localhost:8000/auth/login" \
     -H "Content-Type: application/x-www-form-urlencoded" \
     -d "username=usuario123&password=contraseña123"
```

### 3. Crear categoría (requiere autenticación)

```bash
curl -X POST "http://localhost:8000/categories/" \
      -H "Content-Type: application/json" \
      -H "Authorization: Bearer YOUR_TOKEN" \
      -d '{
        "name": "Alimentación",
        "description": "Gastos en comida y restaurantes",
        "color": "#FF5733",
        "icon": "restaurant",
        "category_type": "expense"
      }'
```

### 4. Crear gasto con categoría (requiere autenticación)

```bash
curl -X POST "http://localhost:8000/expenses/" \
      -H "Content-Type: application/json" \
      -H "Authorization: Bearer YOUR_TOKEN" \
      -d '{
        "amount": 50.00,
        "description": "Cena en restaurante",
        "category_id": 1,
        "date": "2024-01-15T20:30:00Z",
        "tag_ids": [1, 2]
      }'
```

## Endpoints principales

### Autenticación
- `POST /auth/register` - Registro de usuario
- `POST /auth/login` - Inicio de sesión
- `GET /auth/me` - Información del usuario actual

### Categorías
- `POST /categories/` - Crear categoría
- `GET /categories/` - Listar categorías con filtros
- `GET /categories/{id}` - Obtener categoría específica
- `PUT /categories/{id}` - Actualizar categoría
- `DELETE /categories/{id}` - Eliminar categoría

### Métodos de Pago
- `POST /payment-methods/` - Crear método de pago
- `GET /payment-methods/` - Listar métodos de pago
- `GET /payment-methods/{id}` - Obtener método específico
- `PUT /payment-methods/{id}` - Actualizar método
- `DELETE /payment-methods/{id}` - Eliminar método

### Etiquetas
- `POST /tags/` - Crear etiqueta
- `GET /tags/` - Listar etiquetas
- `GET /tags/{id}` - Obtener etiqueta específica
- `PUT /tags/{id}` - Actualizar etiqueta
- `DELETE /tags/{id}` - Eliminar etiqueta

### Gastos
- `POST /expenses/` - Crear gasto
- `GET /expenses/` - Listar gastos
- `GET /expenses/{id}` - Obtener gasto específico
- `PUT /expenses/{id}` - Actualizar gasto
- `DELETE /expenses/{id}` - Eliminar gasto
- `GET /expenses/summary/category` - Resumen por categoría

### Ingresos
- `POST /incomes/` - Crear ingreso
- `GET /incomes/` - Listar ingresos
- `GET /incomes/{id}` - Obtener ingreso específico
- `PUT /incomes/{id}` - Actualizar ingreso
- `DELETE /incomes/{id}` - Eliminar ingreso
- `GET /incomes/summary/source` - Resumen por fuente

### Inversiones
- `POST /investments/` - Crear inversión
- `GET /investments/` - Listar inversiones
- `GET /investments/{id}` - Obtener inversión específica
- `PUT /investments/{id}` - Actualizar inversión
- `DELETE /investments/{id}` - Eliminar inversión
- `GET /investments/summary/type` - Resumen por tipo
- `GET /investments/performance/total` - Rendimiento total

### Productos financieros
- `POST /financial-products/` - Crear producto financiero
- `GET /financial-products/` - Listar productos financieros
- `GET /financial-products/{id}` - Obtener producto específico
- `PUT /financial-products/{id}` - Actualizar producto
- `DELETE /financial-products/{id}` - Eliminar producto
- `GET /financial-products/summary/type` - Resumen por tipo
- `GET /financial-products/balance/total` - Balance total

### Deudas
- `POST /debts/` - Crear deuda
- `GET /debts/` - Listar deudas
- `GET /debts/{id}` - Obtener deuda específica
- `PUT /debts/{id}` - Actualizar deuda
- `DELETE /debts/{id}` - Eliminar deuda
- `PUT /debts/{id}/pay-off` - Marcar deuda como pagada
- `GET /debts/summary/type` - Resumen por tipo
- `GET /debts/balance/total` - Balance total de deudas

### Presupuestos
- `POST /budgets/` - Crear presupuesto
- `GET /budgets/` - Listar presupuestos
- `GET /budgets/{id}` - Obtener presupuesto específico
- `PUT /budgets/{id}` - Actualizar presupuesto
- `DELETE /budgets/{id}` - Eliminar presupuesto
- `POST /budgets/{id}/items/` - Crear ítem de presupuesto
- `PUT /budgets/{id}/items/{item_id}` - Actualizar ítem de presupuesto
- `DELETE /budgets/{id}/items/{item_id}` - Eliminar ítem de presupuesto
- `GET /budgets/{id}/comparison` - Comparación presupuesto vs gastos reales

## Seguridad

- Todos los endpoints (excepto registro) requieren autenticación JWT
- Las contraseñas se almacenan hasheadas con bcrypt
- Los tokens tienen expiración configurable
- Validación estricta de datos de entrada

## Desarrollo

### Estructura del proyecto

```
bk-finance/
├── app/
│   ├── core/
│   │   ├── config.py      # Configuración de la aplicación
│   │   ├── database.py    # Configuración de base de datos
│   │   └── __init__.py
│   ├── models/
│   │   ├── user.py        # Modelo de usuario
│   │   ├── category.py    # Modelo de categorías personalizables
│   │   ├── payment_method.py  # Modelo de métodos de pago
│   │   ├── tag.py         # Modelo de etiquetas
│   │   ├── expense.py     # Modelo de gasto
│   │   ├── income.py      # Modelo de ingreso
│   │   ├── investment.py  # Modelo de inversión
│   │   ├── financial_product.py  # Modelo de producto financiero
│   │   ├── debt.py        # Modelo de deuda
│   │   └── __init__.py
│   ├── routers/
│   │   ├── auth.py        # Endpoints de autenticación
│   │   ├── categories.py  # Endpoints de categorías
│   │   ├── payment_methods.py  # Endpoints de métodos de pago
│   │   ├── tags.py        # Endpoints de etiquetas
│   │   ├── expenses.py    # Endpoints de gastos
│   │   ├── incomes.py     # Endpoints de ingresos
│   │   ├── investments.py # Endpoints de inversiones
│   │   ├── financial_products.py  # Endpoints de productos financieros
│   │   ├── debts.py       # Endpoints de deudas
│   │   └── __init__.py
│   ├── schemas/
│   │   ├── user.py        # Esquemas Pydantic de usuario
│   │   ├── auth.py        # Esquemas Pydantic de autenticación
│   │   ├── category.py    # Esquemas de categorías
│   │   ├── payment_method.py  # Esquemas de métodos de pago
│   │   ├── tag.py         # Esquemas de etiquetas
│   │   ├── expense.py     # Esquemas Pydantic de gasto
│   │   ├── income.py      # Esquemas Pydantic de ingreso
│   │   ├── investment.py  # Esquemas Pydantic de inversión
│   │   ├── financial_product.py  # Esquemas Pydantic de producto financiero
│   │   ├── debt.py        # Esquemas Pydantic de deuda
│   │   └── __init__.py
│   ├── utils/
│   │   ├── auth.py        # Utilidades de autenticación
│   │   └── __init__.py
│   ├── main.py            # Aplicación principal FastAPI
│   └── __init__.py
├── requirements.txt       # Dependencias de Python
├── .env                  # Variables de entorno
└── README.md
```

## Próximas mejoras

- [x] **Categorías personalizables** ✅
- [x] **Métodos de pago personalizables** ✅
- [x] **Etiquetas flexibles** ✅
- [x] **API de presupuestos** ✅
- [x] Tests automatizados ✅
- [ ] Rate limiting
- [ ] Caching con Redis
- [ ] Exportación de datos (PDF, Excel)
- [ ] Notificaciones por email
- [ ] Análisis financieros avanzados
- [ ] Gráficos y dashboards
- [x] **API de presupuestos** ✅
- [ ] Importación de datos desde archivos

## Licencia

Este proyecto está bajo la Licencia MIT.
