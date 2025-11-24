# Diagrama de Clases - Nam Nam Chicken

## Descripción
Este diagrama muestra la estructura de clases del sistema, incluyendo todos los modelos Django, sus atributos, métodos y relaciones.

## Diagrama

![Class Diagram](./images/class_diagram.png)

<details>
<summary>Ver código Mermaid</summary>

```mermaid
classDiagram
    class User {
        <<Django Built-in>>
        +int id
        +string username
        +string email
        +string first_name
        +string last_name
        +string password
        +boolean is_staff
        +boolean is_active
    }

    class Profile {
        +int id
        +User user
        +string address
        +string postal_code
        +string city
        +__str__() string
    }

    class Category {
        +int id
        +string name
        +string slug
        +__str__() string
        +get_absolute_url() string
    }

    class Product {
        +int id
        +Category category
        +string name
        +string slug
        +ImageField image
        +text description
        +decimal price
        +boolean available
        +int stock
        +decimal average_rating
        +int total_reviews
        +datetime created
        +datetime updated
        +get_absolute_url() string
        +__str__() string
    }

    class Review {
        +int id
        +Product product
        +User user
        +int rating
        +text comment
        +datetime created_at
        +__str__() string
    }

    class Order {
        +int id
        +User user
        +string first_name
        +string last_name
        +string email
        +string address
        +string celular
        +text notes
        +datetime created
        +datetime updated
        +boolean paid
        +string status
        +get_total_cost() decimal
        +__str__() string
    }

    class OrderItem {
        +int id
        +Order order
        +Product product
        +decimal price
        +int quantity
        +get_cost() decimal
        +__str__() string
    }

    class Coupon {
        +int id
        +string code
        +int discount_percent
        +datetime valid_from
        +datetime valid_to
        +boolean active
        +int usage_limit
        +int used_count
        +is_valid() boolean
        +__str__() string
    }

    class WishlistItem {
        +int id
        +User user
        +Product product
        +datetime created_at
        +__str__() string
    }

    class Cart {
        <<Non-Model Class>>
        +session session
        +dict cart
        +int coupon_id
        +add(product, quantity, update_quantity)
        +remove(product)
        +clear()
        +apply_coupon(coupon)
        +clear_coupon()
        +get_total_price() decimal
        +get_discount() decimal
        +get_total_price_after_discount() decimal
        +coupon() Coupon
        +__len__() int
        +__iter__()
    }

    %% Relationships
    User "1" -- "1" Profile : has
    User "1" -- "*" Review : writes
    User "1" -- "*" Order : places
    User "1" -- "*" WishlistItem : has

    Category "1" -- "*" Product : contains

    Product "1" -- "*" Review : receives
    Product "1" -- "*" OrderItem : included_in
    Product "1" -- "*" WishlistItem : favorited_by

    Order "1" -- "*" OrderItem : contains

    Cart ..> Product : manages
    Cart ..> Coupon : applies
```

</details>
