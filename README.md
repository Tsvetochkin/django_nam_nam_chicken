# Tienda Online (Nam Nam Chicken)

This is a functional e-commerce project built with Django, simulating an online store for "Nam Nam Chicken".

## Features

*   **Product Management:** List, filter by category, search, and view product details.
*   **Shopping Cart:** Add, modify, remove, view, and clear items in the cart. Cart data is persisted using Django sessions.
*   **User Management:** User registration, login/logout, and user profiles.
*   **Purchase Process:** Order creation with shipping details, simulated payment, order confirmation, and simulated confirmation emails.
*   **Responsive Design:** User interface built with Bootstrap 5.

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

## Installation

1.  **Clone the repository:**
    ```bash
    git clone <repository_url>
    cd django_tienda
    ```
    (Note: Replace `<repository_url>` with the actual repository URL if available)

2.  **Create a virtual environment (recommended):**
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Apply database migrations:**
    ```bash
    python3 manage.py migrate
    ```

5.  **Create a superuser (for Django Admin access):**
    ```bash
    python3 manage.py createsuperuser
    ```

6.  **Collect static files:**
    ```bash
    python3 manage.py collectstatic --noinput
    ```

7.  **Seed initial product data (optional):**
    ```bash
    python3 manage.py seed_products
    ```

## Running the Project

To start the Django development server:

```bash
python3 manage.py runserver
```

Then, open your web browser and navigate to `http://127.0.0.1:8000/`.

## Design Decisions

*   **Framework:** Django for rapid web development and its robust features.
*   **Frontend:** Bootstrap 5 for responsive and modern UI components, complemented by custom CSS for branding and specific layout adjustments.
*   **Shopping Cart:** Implemented using Django sessions for simplicity and ease of use, avoiding immediate database overhead for temporary cart data.
*   **Static Files:** Configured to be served directly by Django's development server in `DEBUG` mode, and collected into `staticfiles/` for production readiness.
*   **Testing:** Comprehensive unit tests cover core functionalities of models, views, and cart logic to ensure reliability and prevent regressions.
*   **Data Seeding:** A custom management command (`seed_products`) is provided for easily populating the database with initial product data, aiding development and testing.
*   **Email Confirmation:** Simulated via Django's console email backend for development, allowing verification of email content without an actual SMTP server.

## Testing

To run the project's test suite:

```bash
python3 manage.py test
```

All tests should pass, ensuring the core functionalities are working correctly.