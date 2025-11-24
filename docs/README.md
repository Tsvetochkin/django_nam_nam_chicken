# Documentación de Diagramas UML - Nam Nam Chicken

## Descripción General
Esta carpeta contiene todos los diagramas UML del proyecto Django Nam Nam Chicken, creados utilizando Mermaid. Los diagramas documentan la arquitectura, diseño y flujos del sistema de e-commerce.

## Índice de Diagramas

### 1. Diagrama de Casos de Uso (8% de la evaluación)
**Archivo**: [use_case_diagram.md](./use_case_diagram.md)

**Descripción**: Muestra las interacciones entre actores (Guest, Registered User, Admin) y los casos de uso del sistema.

**Actores**:
- Guest (Usuario Visitante)
- Registered User (Usuario Registrado)
- Admin (Administrador)

**Casos de Uso Principales**:
- Register, Login/Logout
- Browse Products, Search Products, Filter by Category
- View Product Detail
- Add to Cart, Modify Cart, Remove from Cart, Clear Cart
- Apply Coupon (BONUS)
- Checkout
- View Purchase History (Registered User)
- Manage Wishlist (BONUS - Registered User)
- Post Review (BONUS - Registered User)
- Manage Products, Manage Orders (Admin)

---

### 2. Diagrama de Clases (10% de la evaluación)
**Archivo**: [class_diagram.md](./class_diagram.md)

**Descripción**: Estructura completa de clases del sistema con atributos, métodos y relaciones.

**Clases Principales**:
- **User** (Django Built-in)
- **Profile** - Perfil extendido del usuario
- **Category** - Categorías de productos
- **Product** - Productos del menú
- **Review** - Reseñas de productos (BONUS)
- **Order** - Órdenes de compra
- **OrderItem** - Items de cada orden
- **Coupon** - Cupones de descuento (BONUS)
- **WishlistItem** - Lista de deseos (BONUS)
- **Cart** - Clase no persistente para gestión de carrito

**Relaciones**:
- 1:1 (User-Profile)
- 1:N (Category-Product, User-Order, Order-OrderItem, etc.)
- N:M (User-Product via WishlistItem)

---

### 3. Diagramas de Secuencia (10% de la evaluación)
**Archivo**: [sequence_diagrams.md](./sequence_diagrams.md)

**Descripción**: Seis diagramas que muestran la interacción entre objetos en diferentes flujos.

**Diagramas Incluidos**:
1. **Add Product to Cart** - Agregar producto al carrito
2. **Complete Purchase (Checkout)** - Proceso completo de compra con MercadoPago
3. **Login Process** - Autenticación de usuario
4. **Apply Coupon** (BONUS) - Aplicación de cupones de descuento
5. **Add to Wishlist** (BONUS) - Agregar a lista de deseos
6. **Post Review** (BONUS) - Publicar reseña de producto

**Participantes Principales**:
- User, Views (ProductDetailView, OrderCreateView, etc.)
- Models (Product, Order, OrderItem, Review, Coupon, WishlistItem)
- Cart, Session, MercadoPagoSDK, EmailService

---

### 4. Diagrama Entidad-Relación (7% de la evaluación)
**Archivo**: [er_diagram.md](./er_diagram.md)

**Descripción**: Estructura completa de la base de datos con tablas, campos, tipos, claves y relaciones.

**Tablas Principales**:
- **auth_user** - Usuarios (Django built-in)
- **users_profile** - Perfil extendido
- **users_wishlistitem** - Lista de deseos (BONUS)
- **shop_category** - Categorías
- **shop_product** - Productos
- **shop_review** - Reseñas (BONUS)
- **shop_order** - Órdenes
- **shop_orderitem** - Items de órdenes
- **shop_coupon** - Cupones (BONUS)

**Características Destacadas**:
- Primary Keys (PK), Foreign Keys (FK)
- Índices para optimización
- Unique Constraints
- CHECK Constraints
- CASCADE behaviors
- Cardinalidades detalladas

---

### 5. Diagrama de Máquina de Estados (BONUS)
**Archivo**: [state_machine_diagram.md](./state_machine_diagram.md)

**Descripción**: Ciclo de vida completo de una orden con todas sus transiciones de estado.

**Estados**:
1. **pending** - Pendiente de pago
2. **paid** - Pago confirmado
3. **processing** - En procesamiento
4. **shipped** - Enviado
5. **delivered** - Entregado (estado final exitoso)
6. **cancelled** - Cancelado (estado final de error)

**Transiciones Principales**:
```
pending → paid → processing → shipped → delivered
       ↘ cancelled (desde cualquier estado excepto delivered)
```

**Incluye**:
- Triggers de cada transición
- Acciones en cada estado
- Reglas de negocio
- Casos de uso por estado
- Implementación en código

---

### 6. Diagrama de Actividades (BONUS)
**Archivo**: [activity_diagram.md](./activity_diagram.md)

**Descripción**: Flujo completo del proceso de checkout desde el carrito hasta la confirmación.

**Fases del Flujo**:
1. Validación del carrito
2. Aplicación de cupón (opcional)
3. Verificación de autenticación
4. Completar información de envío
5. Creación de orden
6. Verificación de stock
7. Integración con MercadoPago
8. Procesamiento del pago
9. Actualización de orden
10. Reducción de stock
11. Limpieza de sesión
12. Notificación por email
13. Confirmación al usuario

**Puntos de Decisión**:
- ¿Carrito vacío?
- ¿Desea aplicar cupón?
- ¿Cupón válido?
- ¿Usuario autenticado?
- ¿Formulario válido?
- ¿Stock disponible?
- ¿Pago exitoso?

**Incluye**:
- Swimlanes (responsabilidades)
- Casos de error y recuperación
- Tiempo estimado del flujo
- Mejoras futuras

---

## Características del Proyecto Implementadas

### Funcionalidades Core
✅ Catálogo de productos con categorías
✅ Búsqueda y filtrado de productos
✅ Carrito de compras con gestión de sesión
✅ Checkout con formulario de envío
✅ Integración con MercadoPago para pagos
✅ Gestión de stock automática
✅ Sistema de autenticación (registro, login, logout)
✅ Panel de administración Django

### Funcionalidades BONUS Implementadas
✅ **Reviews** - Sistema de reseñas con ratings (1-5 estrellas)
✅ **Coupons** - Cupones de descuento con validación
✅ **Wishlist** - Lista de deseos para usuarios registrados
✅ **Email Notifications** - Confirmación de órdenes por email
✅ **Purchase History** - Historial de compras
✅ **Guest Checkout** - Compra sin registro

---

## Tecnologías Utilizadas

- **Backend**: Django 5.1.4
- **Database**: SQLite (desarrollo) / PostgreSQL (producción)
- **Payment Gateway**: MercadoPago SDK
- **Email**: Django email backend
- **Frontend**: Django Templates, Bootstrap
- **Diagrams**: Mermaid (Markdown-based)

---

## Cómo Visualizar los Diagramas

### Opción 1: GitHub
Los archivos .md con bloques ```mermaid se renderizarán automáticamente en GitHub.

### Opción 2: VS Code
Instalar extensión "Markdown Preview Mermaid Support":
```bash
code --install-extension bierner.markdown-mermaid
```

### Opción 3: Mermaid Live Editor
Copiar el código Mermaid a: https://mermaid.live/

### Opción 4: Markdown Viewer
Usar cualquier visualizador de Markdown con soporte Mermaid (GitLab, Notion, Obsidian, etc.)

---

## Estructura del Proyecto

```
django_nam_nam_chicken/
├── docs/                           # Esta carpeta
│   ├── README.md                   # Este archivo
│   ├── use_case_diagram.md         # Diagrama de Casos de Uso
│   ├── class_diagram.md            # Diagrama de Clases
│   ├── sequence_diagrams.md        # Diagramas de Secuencia (x6)
│   ├── er_diagram.md               # Diagrama Entidad-Relación
│   ├── state_machine_diagram.md    # Diagrama de Máquina de Estados
│   └── activity_diagram.md         # Diagrama de Actividades
├── shop/                           # App principal
│   ├── models.py                   # Category, Product, Review, Order, OrderItem, Coupon
│   ├── views.py                    # Views del shop
│   ├── urls.py                     # URLs del shop
│   └── ...
├── users/                          # App de usuarios
│   ├── models.py                   # Profile, WishlistItem
│   ├── views.py                    # Views de usuarios
│   └── ...
├── cart/                           # App del carrito
│   ├── cart.py                     # Clase Cart
│   ├── views.py                    # Views del carrito
│   └── ...
└── manage.py
```

---

## Evaluación

### Distribución de Puntos
- **Diagrama de Casos de Uso**: 8%
- **Diagrama de Clases**: 10%
- **Diagramas de Secuencia**: 10% (mínimo 3 diagramas - tenemos 6)
- **Diagrama Entidad-Relación**: 7%
- **Diagramas BONUS**: Puntos adicionales
  - State Machine Diagram
  - Activity Diagram

**Total Base**: 35%
**Total con BONUS**: 35% + puntos extra

---

## Notas Importantes

1. **Precisión**: Todos los diagramas reflejan el código real implementado en el proyecto
2. **Completitud**: Incluyen todas las funcionalidades core + todas las bonus
3. **Formato**: Mermaid Markdown para fácil versionado y renderizado
4. **Documentación**: Cada diagrama incluye explicaciones detalladas
5. **Relaciones**: Todos los diagramas están interconectados y consistentes

---

## Autor

**Proyecto**: Django Nam Nam Chicken
**Curso**: Desarrollo de Aplicaciones Web
**Institución**: Da Vinci
**Fecha**: Noviembre 2024

---

## Referencias

- [Mermaid Documentation](https://mermaid.js.org/)
- [Django Documentation](https://docs.djangoproject.com/)
- [MercadoPago SDK](https://www.mercadopago.com.ar/developers/)
- [UML Diagrams Guide](https://www.uml-diagrams.org/)