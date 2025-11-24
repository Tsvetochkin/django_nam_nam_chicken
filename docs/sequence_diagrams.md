# Diagramas de Secuencia - Nam Nam Chicken

## Descripción
Estos diagramas muestran la interacción entre objetos en diferentes flujos del sistema.

## 1. Agregar Producto al Carrito

```mermaid
sequenceDiagram
    actor User
    participant ProductDetailView
    participant CartAddProductForm
    participant Cart
    participant Session
    participant Product

    User->>ProductDetailView: POST /cart/add/{product_id}
    ProductDetailView->>CartAddProductForm: validate form data
    CartAddProductForm-->>ProductDetailView: cleaned_data
    ProductDetailView->>Product: get_object_or_404(id)
    Product-->>ProductDetailView: product instance
    ProductDetailView->>Cart: __init__(request)
    Cart->>Session: get(CART_SESSION_ID)
    Session-->>Cart: cart dict
    ProductDetailView->>Cart: add(product, quantity, update)
    Cart->>Cart: update cart dict
    Cart->>Session: modified = True
    Cart-->>ProductDetailView: success
    ProductDetailView->>User: redirect to cart_detail
    ProductDetailView->>User: show success message
```

## 2. Completar Compra (Checkout)

```mermaid
sequenceDiagram
    actor User
    participant OrderCreateView
    participant OrderCreateForm
    participant Order
    participant OrderItem
    participant Product
    participant MercadoPagoSDK
    participant EmailService
    participant Cart

    User->>OrderCreateView: POST /shop/order/create
    OrderCreateView->>Cart: __init__(request)
    Cart-->>OrderCreateView: cart instance
    OrderCreateView->>OrderCreateForm: validate form data
    OrderCreateForm-->>OrderCreateView: valid order data
    OrderCreateView->>Order: create(first_name, last_name, email, address)
    Order-->>OrderCreateView: order instance

    loop For each cart item
        OrderCreateView->>OrderItem: create(order, product, price, quantity)
        OrderItem-->>OrderCreateView: item created
    end

    OrderCreateView->>MercadoPagoSDK: create preference
    MercadoPagoSDK-->>OrderCreateView: preference_id
    OrderCreateView->>User: render payment page

    User->>MercadoPagoSDK: complete payment
    MercadoPagoSDK->>OrderCreateView: payment_success callback
    OrderCreateView->>Order: set paid=True, status='paid'

    loop For each order item
        OrderCreateView->>Product: decrease stock
        Product-->>OrderCreateView: stock updated
    end

    OrderCreateView->>EmailService: send_mail(confirmation)
    EmailService-->>User: order confirmation email
    OrderCreateView->>Cart: clear()
    OrderCreateView->>User: show success page
```

## 3. Proceso de Login

```mermaid
sequenceDiagram
    actor User
    participant LoginView
    participant AuthBackend
    participant Session
    participant Profile
    participant Database

    User->>LoginView: POST /users/login
    LoginView->>AuthBackend: authenticate(username, password)
    AuthBackend->>Database: query User table
    Database-->>AuthBackend: user found
    AuthBackend-->>LoginView: authenticated user
    LoginView->>Session: create session
    Session->>Database: store session data
    Database-->>Session: session created
    LoginView->>Profile: get_or_create(user)
    Profile-->>LoginView: profile instance
    LoginView->>User: redirect to product_list
    LoginView->>User: show success message
```

## 4. Aplicar Cupón (BONUS)

```mermaid
sequenceDiagram
    actor User
    participant CartView
    participant Coupon
    participant Cart
    participant Session

    User->>CartView: POST /cart/apply-coupon
    CartView->>CartView: get coupon_code from POST
    CartView->>Coupon: get(code__iexact=coupon_code)
    Coupon-->>CartView: coupon instance
    CartView->>Coupon: is_valid()

    alt Coupon is valid
        Coupon-->>CartView: True
        CartView->>Cart: apply_coupon(coupon)
        Cart->>Session: set coupon_id
        Session-->>Cart: saved
        CartView->>Coupon: used_count += 1
        Coupon->>Coupon: save()
        CartView->>Cart: get_discount()
        Cart-->>CartView: discount amount
        CartView->>User: show success message
    else Coupon is invalid
        Coupon-->>CartView: False
        CartView->>User: show error message
    end

    CartView->>User: redirect to cart_detail
```

## 5. Agregar a Lista de Deseos (BONUS)

```mermaid
sequenceDiagram
    actor User
    participant WishlistAddView
    participant Product
    participant WishlistItem
    participant Database

    User->>WishlistAddView: POST /users/wishlist/add/{product_id}
    WishlistAddView->>WishlistAddView: check user.is_authenticated
    WishlistAddView->>Product: get_object_or_404(id)
    Product-->>WishlistAddView: product instance
    WishlistAddView->>WishlistItem: get_or_create(user, product)
    WishlistItem->>Database: check unique_together constraint

    alt Item created
        Database-->>WishlistItem: created=True
        WishlistItem-->>WishlistAddView: (item, True)
        WishlistAddView->>User: show success message
    else Item exists
        Database-->>WishlistItem: created=False
        WishlistItem-->>WishlistAddView: (item, False)
        WishlistAddView->>User: show info message
    end

    WishlistAddView->>User: redirect to previous page
```

## 6. Publicar Reseña (BONUS)

```mermaid
sequenceDiagram
    actor User
    participant ProductDetailView
    participant ReviewForm
    participant Review
    participant Product
    participant Database

    User->>ProductDetailView: POST /shop/{id}/{slug}/
    ProductDetailView->>ProductDetailView: check user.is_authenticated
    ProductDetailView->>Review: filter(product, user).first()

    alt Review exists
        Review-->>ProductDetailView: existing_review
        ProductDetailView->>ReviewForm: ReviewForm(POST, instance=existing_review)
    else No review
        Review-->>ProductDetailView: None
        ProductDetailView->>ReviewForm: ReviewForm(POST)
    end

    ProductDetailView->>ReviewForm: is_valid()
    ReviewForm-->>ProductDetailView: True
    ProductDetailView->>Review: save(commit=False)
    Review->>Review: set product and user
    Review->>Database: save()
    Database-->>Review: saved
    ProductDetailView->>User: show success message
    ProductDetailView->>User: redirect to product detail
```

## Explicación de Elementos Clave

### Actores y Participantes
- **User**: El usuario final del sistema
- **Views**: Controladores Django que manejan las peticiones HTTP
- **Models**: Clases de modelo Django que representan entidades de la base de datos
- **Cart**: Clase auxiliar para gestionar el carrito de compras en sesión
- **Session**: Sistema de sesiones de Django
- **MercadoPagoSDK**: SDK de integración con pasarela de pagos
- **EmailService**: Servicio de envío de correos electrónicos

### Flujos Principales
1. **Add to Cart**: Gestión de productos en carrito mediante sesión
2. **Checkout**: Proceso completo de compra con reducción de stock y confirmación
3. **Login**: Autenticación de usuario con creación de perfil automática
4. **Apply Coupon**: Validación y aplicación de cupones de descuento
5. **Wishlist**: Gestión de lista de deseos con prevención de duplicados
6. **Review**: Publicación y edición de reseñas de productos
