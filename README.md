# 🍗 Nam Nam Chicken - E-Commerce System

Sistema de carrito de compras desarrollado con Django 4.2+ para el Trabajo Práctico de Análisis y Metodología de Sistemas.

## 📋 Características

### Funcionalidades Core
- **Gestión de Productos:** Lista con filtros por categoría, búsqueda por texto, vista de detalles
- **Carrito de Compras:** Agregar/modificar/eliminar productos, cálculo de totales, persistencia en sesión
- **Gestión de Usuarios:** Registro, autenticación, perfil con datos personales, historial de pedidos
- **Proceso de Compra:** Formulario de envío, integración de pago, confirmación con número de orden, email de confirmación
- **Responsive Design:** Interfaz con Bootstrap 5

### Funcionalidades Adicionales
- **Sistema de Reviews:** Calificación y comentarios de productos
- **Sistema de Cupones:** Descuentos mediante códigos promocionales
- **Lista de Deseos:** Guardar productos para compra posterior
- **Integración MercadoPago:** Pasarela de pagos en modo test
- **Seguimiento de Pedidos:** Estados (pending, paid, processing, shipped, delivered, cancelled)
- **Gestión de Inventario:** Reducción automática de stock al confirmar pago

## 📁 Estructura del Proyecto

```
django_nam_nam_chicken/
├── manage.py
├── pytest.ini                    # Configuración de pytest
├── requirements.txt              # Dependencias del proyecto
├── .gitignore
│
├── tienda_online/                # Configuración principal de Django
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
│
├── shop/                         # App principal de e-commerce
│   ├── migrations/
│   ├── management/
│   │   └── commands/
│   │       └── seed_products.py  # Comando para cargar datos de prueba
│   ├── templates/shop/
│   ├── static/shop/
│   ├── models.py                 # Category, Product, Review, Order, OrderItem, Coupon
│   ├── views.py
│   ├── forms.py
│   ├── admin.py
│   └── urls.py
│
├── cart/                         # App de carrito de compras
│   ├── templates/cart/
│   ├── cart.py                   # Lógica del carrito (session-based)
│   ├── views.py
│   ├── forms.py
│   ├── context_processors.py
│   └── urls.py
│
├── users/                        # App de gestión de usuarios
│   ├── migrations/
│   ├── templates/users/
│   ├── models.py                 # Profile, WishlistItem
│   ├── views.py
│   ├── forms.py
│   ├── admin.py
│   └── urls.py
│
├── tests/                        # Suite de tests con pytest
│   ├── conftest.py
│   ├── test_products.py
│   ├── test_cart.py
│   ├── test_orders.py
│   ├── test_users.py
│   ├── test_reviews.py
│   ├── test_security.py
│   ├── test_integration.py
│   └── test_admin.py
│
├── docs/                         # Documentación y diagramas
│   ├── images/                   # Diagramas en formato PNG
│   ├── README.md                 # Índice de documentación
│   ├── use_case_diagram.md
│   ├── class_diagram.md
│   ├── sequence_diagrams.md
│   ├── er_diagram.md
│   ├── state_machine_diagram.md
│   └── activity_diagram.md
│
├── static/
├── staticfiles/
├── media/
└── db.sqlite3
```

## 📚 Documentación

Todos los diagramas UML están disponibles en la carpeta [`/docs`](./docs/) en dos formatos:
- **Código Mermaid** (.md) para versionamiento y edición
- **Imágenes PNG** (.png) para visualización universal

### Diagramas Disponibles

| Diagrama | Archivo MD | Imagen PNG |
|----------|-----------|------------|
| **Casos de Uso** | [MD](./docs/use_case_diagram.md) | [PNG](./docs/images/use_case_diagram.png) |
| **Clases** | [MD](./docs/class_diagram.md) | [PNG](./docs/images/class_diagram.png) |
| **Secuencia (x6)** | [MD](./docs/sequence_diagrams.md) | [Ver 6 PNG](./docs/images/) |
| **Entidad-Relación** | [MD](./docs/er_diagram.md) | [PNG](./docs/images/er_diagram.png) |
| **Máquina de Estados** | [MD](./docs/state_machine_diagram.md) | [PNG](./docs/images/state_machine.png) |
| **Actividades** | [MD](./docs/activity_diagram.md) | [PNG](./docs/images/activity_diagram.png) |

📂 **[Índice completo de documentación](./docs/README.md)**

## 🚀 Instalación y Configuración

### Requisitos Previos
- Python 3.11+
- uv (Python package manager)

### Instalación

1. **Clonar el repositorio:**
   ```bash
   git clone <repository_url>
   cd django_nam_nam_chicken
   ```

2. **Instalar dependencias con uv:**
   ```bash
   uv pip install -r requirements.txt
   ```

3. **Aplicar migraciones:**
   ```bash
   uv run python manage.py migrate
   ```

4. **Crear superusuario (para acceso al Admin):**
   ```bash
   uv run python manage.py createsuperuser
   ```

5. **Cargar datos de prueba:**
   ```bash
   uv run python manage.py seed_products
   ```

### Ejecutar el Proyecto

```bash
uv run python manage.py runserver
```

Abrir navegador en `http://127.0.0.1:8000/`

## 👤 Usuarios de Prueba

El sistema incluye usuarios pre-configurados para facilitar las pruebas:

| Usuario | Contraseña | Rol | Uso |
|---------|-----------|-----|-----|
| `admin` | `admin123` | Administrador | Acceso completo al panel de administración |
| `testuser` | `test123` | Usuario regular | Pruebas de funcionalidad de cliente |
| `apro` | `apro123` | Usuario regular | Pruebas de MercadoPago (usar con tarjeta APRO) |

### Acceso al Admin

- **URL:** `http://127.0.0.1:8000/admin/`
- **Usuario:** `admin`
- **Contraseña:** `admin123`

## 💳 Pruebas de MercadoPago

El sistema está configurado en **modo test** con credenciales de sandbox. Para probar pagos:

### Tarjetas de Prueba

| Tipo | Número | CVV | Vencimiento |
|------|--------|-----|-------------|
| Visa | `4509 9535 6623 3704` | `123` | `11/30` |
| Mastercard | `5031 7557 3453 0604` | `123` | `11/30` |

### Datos del Titular (para aprobación)

Para que el pago sea **aprobado**, usar:
- **Nombre:** `APRO`
- **Documento:** `12345678`

### Otros Escenarios de Prueba

| Nombre | Resultado |
|--------|-----------|
| `APRO` | Pago aprobado ✅ |
| `OTHE` | Rechazado por error general |
| `CONT` | Pago pendiente |
| `CALL` | Rechazado - requiere autorización |

## 🎟️ Cupones de Descuento

Cupones activos para pruebas:

| Código | Descuento | Validez |
|--------|-----------|---------|
| `WELCOME10` | 10% | 365 días |
| `VERANO20` | 20% | 90 días |
| `PROMO15` | 15% | 30 días |

## 🧪 Testing

Ejecutar la suite de tests:

```bash
uv run pytest
```

Ejecutar tests con cobertura:

```bash
uv run pytest --cov=shop --cov=cart --cov=users
```

La suite incluye tests unitarios, de integración y de seguridad. Ver [`/tests`](./tests/) para detalles.

## 🛠 Tecnologías Utilizadas

- **Backend:** Django 4.2.26, Python 3.11+
- **Frontend:** HTML5, CSS3, Bootstrap 5, JavaScript
- **Base de Datos:** SQLite (desarrollo)
- **Pagos:** MercadoPago SDK 2.2.3
- **Testing:** pytest 8.3.4, pytest-django 4.9.0
- **Package Manager:** uv
- **Version Control:** Git

## 📐 Decisiones de Diseño

- **Framework Django:** Desarrollo rápido con funcionalidades robustas out-of-the-box
- **Bootstrap 5:** UI responsive y moderna con componentes reutilizables
- **Session-based Cart:** Simplicidad y performance, sin overhead de DB para datos temporales
- **Signal-based Profile:** Creación automática de perfil al registrar usuario
- **MercadoPago Checkout:** Integración segura con redirect flow y webhooks preparados
- **pytest:** Framework moderno de testing con fixtures y mejor DX que unittest
- **Mermaid Diagrams:** Diagramas como código, versionables y renderizables en GitHub
- **Email Console Backend:** Verificación de emails sin SMTP server durante desarrollo
- **Management Command:** Seeding de datos de prueba con `seed_products`

---

**Desarrollado para Trabajo Práctico - Análisis y Metodología de Sistemas**

*Fecha de entrega: 25/11/2025*

Ver [reporte de completitud](./docs/COMPLETION_REPORT.md) para detalles sobre el cumplimiento de requisitos.
