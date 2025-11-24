# Diagrama Entidad-Relación - Nam Nam Chicken

## Descripción
Este diagrama muestra la estructura de la base de datos con todas las tablas, sus campos, tipos de datos, claves primarias (PK), claves foráneas (FK) y relaciones.

```mermaid
erDiagram
    auth_user ||--o| users_profile : "has"
    auth_user ||--o{ users_wishlistitem : "has"
    auth_user ||--o{ shop_review : "writes"
    auth_user ||--o{ shop_order : "places"

    shop_category ||--o{ shop_product : "contains"

    shop_product ||--o{ shop_review : "receives"
    shop_product ||--o{ shop_orderitem : "included_in"
    shop_product ||--o{ users_wishlistitem : "favorited_in"

    shop_order ||--|{ shop_orderitem : "contains"

    auth_user {
        int id PK
        string username UK "UNIQUE, NOT NULL"
        string password "NOT NULL"
        string email
        string first_name
        string last_name
        boolean is_staff "DEFAULT FALSE"
        boolean is_active "DEFAULT TRUE"
        boolean is_superuser "DEFAULT FALSE"
        datetime date_joined "NOT NULL"
        datetime last_login
    }

    users_profile {
        int id PK
        int user_id FK "UNIQUE, NOT NULL"
        string address "VARCHAR(250)"
        string postal_code "VARCHAR(20)"
        string city "VARCHAR(100)"
    }

    users_wishlistitem {
        int id PK
        int user_id FK "NOT NULL, INDEX"
        int product_id FK "NOT NULL, INDEX"
        datetime created_at "NOT NULL, AUTO"
    }

    shop_category {
        int id PK
        string name "VARCHAR(200), NOT NULL, INDEX"
        string slug "VARCHAR(200), UNIQUE, NOT NULL"
    }

    shop_product {
        int id PK
        int category_id FK "NOT NULL"
        string name "VARCHAR(200), NOT NULL, INDEX"
        string slug "VARCHAR(200), NOT NULL"
        string image "VARCHAR(100)"
        text description
        decimal price "DECIMAL(10,2), NOT NULL"
        boolean available "DEFAULT TRUE"
        int stock "UNSIGNED INT, DEFAULT 0"
        decimal average_rating "DECIMAL(3,2), DEFAULT 0.00"
        int total_reviews "UNSIGNED INT, DEFAULT 0"
        datetime created "NOT NULL, AUTO, INDEX DESC"
        datetime updated "NOT NULL, AUTO"
    }

    shop_review {
        int id PK
        int product_id FK "NOT NULL, INDEX"
        int user_id FK "NOT NULL, INDEX"
        int rating "INT, NOT NULL, CHECK 1-5"
        text comment
        datetime created_at "NOT NULL, AUTO, INDEX DESC"
    }

    shop_order {
        int id PK
        int user_id FK "NULL, INDEX"
        string first_name "VARCHAR(50), NOT NULL"
        string last_name "VARCHAR(50), NOT NULL"
        string email "VARCHAR(254), NOT NULL"
        string address "VARCHAR(250), NOT NULL"
        string celular "VARCHAR(20)"
        text notes
        datetime created "NOT NULL, AUTO, INDEX DESC"
        datetime updated "NOT NULL, AUTO"
        boolean paid "DEFAULT FALSE"
        string status "VARCHAR(20), DEFAULT 'pending'"
    }

    shop_orderitem {
        int id PK
        int order_id FK "NOT NULL, INDEX"
        int product_id FK "NOT NULL, INDEX"
        decimal price "DECIMAL(10,2), NOT NULL"
        int quantity "UNSIGNED INT, DEFAULT 1"
    }

    shop_coupon {
        int id PK
        string code "VARCHAR(50), UNIQUE, NOT NULL"
        int discount_percent "INT, NOT NULL, CHECK 0-100"
        datetime valid_from "NOT NULL"
        datetime valid_to "NOT NULL"
        boolean active "DEFAULT TRUE"
        int usage_limit "UNSIGNED INT, DEFAULT 1"
        int used_count "UNSIGNED INT, DEFAULT 0"
    }
```

## Explicación de Tablas y Relaciones

### Tablas Principales

#### auth_user (Django Built-in)
- **PK**: id (AutoField)
- **Unique Keys**: username
- **Descripción**: Tabla estándar de usuarios de Django
- **Relaciones**:
  - 1:1 con users_profile
  - 1:N con users_wishlistitem, shop_review, shop_order

#### users_profile
- **PK**: id (AutoField)
- **FK**: user_id → auth_user.id (OneToOne)
- **Unique Constraints**: user_id (único por usuario)
- **Descripción**: Perfil extendido del usuario con información de dirección
- **Trigger**: Se crea automáticamente al crear un usuario (signal post_save)

#### shop_category
- **PK**: id (AutoField)
- **Unique Keys**: slug
- **Indexes**: name
- **Descripción**: Categorías de productos (ej: "Chicken", "Burgers", "Sides")

#### shop_product
- **PK**: id (AutoField)
- **FK**: category_id → shop_category.id
- **Indexes**:
  - (id, slug) - compuesto
  - name
  - created (descendente)
- **Descripción**: Productos del menú con stock, precio y ratings
- **Business Logic**:
  - available controla visibilidad
  - stock se decrementa en cada venta exitosa
  - average_rating y total_reviews se actualizan con reviews

#### shop_review
- **PK**: id (AutoField)
- **FK**:
  - product_id → shop_product.id
  - user_id → auth_user.id
- **Unique Constraints**: (product_id, user_id) - un usuario solo puede hacer una review por producto
- **Indexes**: created_at (descendente)
- **Validations**: rating debe estar entre 1 y 5

#### shop_order
- **PK**: id (AutoField)
- **FK**: user_id → auth_user.id (nullable, SET_NULL)
- **Indexes**: created (descendente)
- **Descripción**: Órdenes de compra
- **Status Flow**: pending → paid → processing → shipped → delivered
- **Business Logic**:
  - user_id puede ser NULL (órdenes de guests)
  - paid se marca True después del pago exitoso
  - status se actualiza durante el ciclo de vida del pedido

#### shop_orderitem
- **PK**: id (AutoField)
- **FK**:
  - order_id → shop_order.id (CASCADE)
  - product_id → shop_product.id (CASCADE)
- **Descripción**: Items individuales de cada orden
- **Business Logic**:
  - price se guarda para mantener histórico (puede diferir del precio actual)
  - CASCADE delete: si se borra la orden, se borran los items

#### users_wishlistitem
- **PK**: id (AutoField)
- **FK**:
  - user_id → auth_user.id (CASCADE)
  - product_id → shop_product.id (CASCADE)
- **Unique Constraints**: (user_id, product_id) - un producto solo puede estar una vez en la wishlist
- **Indexes**: created_at (descendente)

#### shop_coupon
- **PK**: id (AutoField)
- **Unique Keys**: code
- **Indexes**: valid_from (descendente)
- **Descripción**: Cupones de descuento
- **Validations**:
  - discount_percent entre 0 y 100
  - usage_limit controla uso máximo
  - used_count incrementa con cada uso
- **Business Logic**: is_valid() verifica active, fechas y límite de uso

### Cardinalidades

- **1:1**: auth_user ↔ users_profile
- **1:N**:
  - auth_user → shop_review
  - auth_user → shop_order
  - auth_user → users_wishlistitem
  - shop_category → shop_product
  - shop_product → shop_review
  - shop_product → shop_orderitem
  - shop_product → users_wishlistitem
  - shop_order → shop_orderitem
- **N:M** (via tabla intermedia):
  - auth_user ↔ shop_product (via users_wishlistitem)

### Índices y Optimizaciones

1. **Índices Simples**:
   - shop_category: name
   - shop_product: name, created (DESC)
   - shop_review: created_at (DESC)
   - shop_order: created (DESC)
   - users_wishlistitem: created_at (DESC)

2. **Índices Compuestos**:
   - shop_product: (id, slug) - para URLs amigables

3. **Índices de Foreign Keys**:
   - Django crea automáticamente índices en todas las FK

4. **Unique Constraints**:
   - shop_review: (product_id, user_id)
   - users_wishlistitem: (user_id, product_id)

### Constraints y Validaciones

1. **NOT NULL**:
   - Todos los campos requeridos para operación del negocio

2. **CHECK Constraints**:
   - shop_review.rating: 1 ≤ rating ≤ 5
   - shop_coupon.discount_percent: 0 ≤ discount_percent ≤ 100

3. **DEFAULT Values**:
   - Boolean fields: False/True según lógica de negocio
   - Integer counters: 0
   - Status: 'pending'

4. **CASCADE Behaviors**:
   - shop_orderitem → shop_order: CASCADE (borrar orden borra items)
   - shop_product → shop_category: CASCADE (borrar categoría borra productos)
   - users_wishlistitem: CASCADE en ambas FK
   - shop_order.user_id: SET_NULL (preservar órdenes de usuarios borrados)