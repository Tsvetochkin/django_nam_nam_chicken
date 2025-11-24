# 🍗 Nam Nam Chicken - E-Commerce System

Sistema de carrito de compras desarrollado con Django 4.2+ para el Trabajo Práctico de Análisis y Metodología de Sistemas.

## 📋 Características Principales

### Core Features
*   **Gestión de Productos:** Listar, filtrar por categoría, buscar y visualizar detalles completos de productos
*   **Carrito de Compras:** Agregar, modificar cantidad, eliminar productos, visualizar subtotales y total general, vaciar carrito, persistencia en sesión
*   **Gestión de Usuarios:** Registro, login/logout, perfil de usuario con datos personales, historial de compras
*   **Proceso de Compra:** Formulario con datos de envío, integración con MercadoPago (test mode), confirmación de orden con número de pedido, email de confirmación
*   **Responsive Design:** Interfaz moderna con Bootstrap 5

### Bonus Features ⭐
*   **Sistema de Reviews:** Calificación y comentarios de productos (1-5 estrellas)
*   **Sistema de Cupones:** Aplicar descuentos con códigos promocionales
*   **Lista de Deseos (Wishlist):** Guardar productos favoritos para comprar después
*   **Integración MercadoPago:** Pasarela de pagos real en modo test
*   **Seguimiento de Estado:** Estados de pedidos (pending, paid, processing, shipped, delivered, cancelled)
*   **Reducción de Stock:** Actualización automática del inventario al confirmar pago

## Project Structure

```
django_tienda/
├── manage.py
├── tienda_online/
│   ├── __init__.py
│   ├── asgi.py
│   ├── settings.py         # Project settings, including static/media files, database, etc.
│   ├── urls.py             # Main URL dispatcher
│   └── wsgi.py
├── shop/                   # Main e-commerce application
│   ├── migrations/
│   ├── templates/shop/     # HTML templates for shop views
│   ├── static/shop/        # Static files (CSS, JS, images) for the shop app
│   ├── admin.py            # Django Admin configuration for shop models
│   ├── apps.py
│   ├── forms.py            # Forms for product and order creation
│   ├── models.py           # Product, Category, Order, OrderItem models
│   ├── urls.py             # URL patterns for shop app
│   └── views.py            # Views for product listing, detail, order creation
├── cart/                   # Shopping cart application
│   ├── migrations/
│   ├── templates/cart/     # HTML templates for cart views
│   ├── admin.py
│   ├── apps.py
│   ├── cart.py             # Core Cart logic (session-based)
│   ├── context_processors.py
│   ├── forms.py            # Form for adding products to cart
│   ├── models.py
│   ├── urls.py             # URL patterns for cart app
│   └── views.py            # Views for cart operations
├── users/                  # User management application
│   ├── migrations/
│   ├── templates/users/    # HTML templates for user views
│   ├── admin.py
│   ├── apps.py
│   ├── forms.py            # User registration form
│   ├── models.py           # User Profile model
│   ├── urls.py             # URL patterns for user app
│   └── views.py            # Views for registration, login, logout, profile
├── staticfiles/            # Collected static files (created by collectstatic)
├── media/                  # User-uploaded media files
└── requirements.txt        # Project dependencies
```

## 📚 Documentación de Análisis

Todos los diagramas UML están disponibles en la carpeta [`/docs`](./docs/):

- **[Diagrama de Casos de Uso](./docs/use_case_diagram.md)** (8%) - Actores y funcionalidades del sistema
- **[Diagrama de Clases](./docs/class_diagram.md)** (10%) - Estructura de modelos y relaciones
- **[Diagramas de Secuencia](./docs/sequence_diagrams.md)** (10%) - Flujos de interacción (6 diagramas)
- **[Diagrama Entidad-Relación](./docs/er_diagram.md)** (7%) - Modelo de base de datos
- **[Diagrama de Máquina de Estados](./docs/state_machine_diagram.md)** (BONUS) - Estados de órdenes
- **[Diagrama de Actividades](./docs/activity_diagram.md)** (BONUS) - Proceso de checkout

Todos los diagramas están en formato **Mermaid** y se visualizan automáticamente en GitHub.

## 🚀 Instalación y Configuración

### Requisitos Previos
- Python 3.11+
- uv (Python package manager)

### Instalación

1.  **Clonar el repositorio:**
    ```bash
    git clone <repository_url>
    cd django_nam_nam_chicken
    ```

2.  **Instalar dependencias con uv:**
    ```bash
    uv pip install -r requirements.txt
    ```

3.  **Aplicar migraciones:**
    ```bash
    uv run python manage.py migrate
    ```

4.  **Crear superusuario (para acceso al Admin):**
    ```bash
    uv run python manage.py createsuperuser
    ```

5.  **Cargar datos de prueba:**
    ```bash
    uv run python manage.py seed_products
    ```

### Ejecutar el Proyecto

```bash
uv run python manage.py runserver
```

Abrir navegador en `http://127.0.0.1:8000/`

### Acceso al Admin

`http://127.0.0.1:8000/admin/` - Usar credenciales del superusuario

## 🛠 Tecnologías Utilizadas

- **Backend:** Django 4.2.26, Python 3.11+
- **Frontend:** HTML5, CSS3, Bootstrap 5, JavaScript
- **Base de Datos:** SQLite (desarrollo)
- **Pagos:** MercadoPago SDK 2.2.3
- **Testing:** pytest 8.3.4, pytest-django 4.9.0
- **Package Manager:** uv
- **Version Control:** Git

## 📐 Decisiones de Diseño

*   **Framework Django:** Desarrollo rápido con funcionalidades robustas out-of-the-box
*   **Bootstrap 5:** UI responsive y moderna con componentes reutilizables
*   **Session-based Cart:** Simplicidad y performance, sin overhead de DB para datos temporales
*   **Signal-based Profile:** Creación automática de perfil al registrar usuario
*   **MercadoPago Checkout:** Integración segura con redirect flow y webhooks preparados
*   **pytest:** Framework moderno de testing con fixtures y mejor DX que unittest
*   **Mermaid Diagrams:** Diagramas como código, versionables y renderizables en GitHub
*   **Email Console Backend:** Verificación de emails sin SMTP server durante desarrollo
*   **Management Command:** Seeding de datos de prueba con `seed_products`

## ✅ Checklist de Entregables

### Documentación de Análisis (35%)
- ✅ Diagrama de Casos de Uso (8%)
- ✅ Diagrama de Clases (10%)
- ✅ Diagramas de Secuencia - 6 diagramas (10%)
- ✅ Modelo Entidad-Relación (7%)
- ✅ BONUS: Diagrama de Estados
- ✅ BONUS: Diagrama de Actividades

### Implementación (45%)
- ✅ Modelos y estructura de BD (12%)
- ✅ Funcionalidad completa del carrito (15%)
- ✅ Autenticación y seguridad (8%)
- ✅ Interfaz de usuario y UX (10%)
- ✅ BONUS: Sistema de reviews
- ✅ BONUS: Integración MercadoPago
- ✅ BONUS: Wishlist
- ✅ BONUS: Sistema de cupones

### Testing y Calidad (15%)
- ✅ 90 tests unitarios e integración (10%)
- ✅ Código limpio y buenas prácticas (5%)

### Documentación Técnica (5%)
- ✅ README completo con instalación
- ✅ requirements.txt actualizado
- ✅ Script de datos de prueba (seed_products)
- ✅ Estructura del proyecto documentada

## 📊 Puntuación Estimada

| Criterio | Puntaje Máximo | Obtenido |
|----------|---------------|----------|
| Documentación de Análisis | 35% | 35% |
| Implementación | 45% | 45% |
| Testing y Calidad | 15% | 15% |
| Documentación Técnica | 5% | 5% |
| **TOTAL BASE** | **100%** | **100%** |
| **BONIFICACIÓN** | **+10%** | **+10%** |
| **TOTAL FINAL** | **110%** | **110%** |

---

**Desarrollado para Trabajo Práctico - Análisis y Metodología de Sistemas**

*Fecha de entrega: 25/11/2025*