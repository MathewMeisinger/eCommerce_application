# eCommerce Application

## Overview

This project is a multi-app Django eCommerce application that supports buyers, vendors, stores, products, carts, orders, reviews, REST API endpoints, and X/Twitter integration. It extends a marketplace-style workflow where vendors can create stores and products, buyers can browse listings and place orders, and selected events can trigger social media posts.

This version of the project includes both traditional Django views/templates and API endpoints for stores and products. It also includes email-based invoice sending during checkout and X/Twitter posting through the Tweepy client.

## Main Functionality

### User Accounts and Roles

The project uses a custom user model with two roles:

- **Buyer**
- **Vendor**

Role-specific behavior is used throughout the app:

- vendors can create and manage stores and products,
- buyers can browse products, add items to a cart, review products, and check out.

### Stores

Vendors can:

- create stores,
- view their own stores,
- update store details,
- delete stores.

When a store is deleted, its products are first soft-deleted by marking them inactive before the store record is removed.

### Products

Vendors can:

- create products for their stores,
- edit their own products,
- soft-delete products by marking them inactive.

Buyers can:

- browse active products,
- search for products,
- view product details,
- leave reviews.

### Reviews

Buyers can leave product reviews from the product detail page.

The project also flags whether a review is **verified** by checking if the user has previously purchased that product through an order.

### Cart and Orders

Buyers can:

- add items to a cart,
- update quantities,
- remove items,
- proceed to checkout.

During checkout, the application:

- validates available stock,
- creates an order,
- creates related order items,
- reduces stock levels,
- clears the cart,
- sends an invoice email.

### Email Invoice Integration

When a buyer completes checkout, the application renders an invoice email from a template and sends it using Django’s email system.

In the current settings, email is configured to print to the console for development.

## API Integration

The project includes Django REST Framework API endpoints for stores and products.

### Store API

Available under:

- `api/stores/`
- `api/stores/create/`

These endpoints allow:

- listing stores,
- creating a store as an authenticated vendor.

### Product API

Available under:

- `api/products/`
- `api/products/create/<store_id>/`
- `api/products/<product_id>/reviews/`

These endpoints allow:

- listing active products,
- creating products for a vendor-owned store,
- listing reviews for a product.

### Authentication for the API

The API is configured with Django REST Framework and uses **Basic Authentication** by default for protected endpoints.

Protected creation endpoints also check permissions in view logic, for example:

- only authenticated users may create stores/products,
- only vendors may create stores/products,
- vendors may only create products for stores they own.

The project also contains JWT-related settings, which suggest token support was being prepared or extended, but the current default REST framework configuration uses Basic Authentication.

## X/Twitter Integration

The project includes a dedicated integration module:

- `integrations/twitter.py`

This module uses **Tweepy** and credentials loaded from environment variables in `settings.py`.

### What triggers an X/Twitter post?

An X/Twitter post is attempted when:

- a new store is created,
- a new product is created.

This happens from both:

- standard Django view workflows,
- API creation workflows.

### How it works

1. A store or product is created successfully.
2. The relevant helper function is called:
   - `tweet_new_store(store_id)`
   - `tweet_new_product(product_id)`
3. The helper fetches the created object from the database.
4. It builds a short message.
5. It creates a Tweepy client using credentials from Django settings.
6. It sends the post with `client.create_tweet(...)`.

### Required Environment Variables

The following variables are read in `settings.py`:

- `X_CONSUMER_KEY`
- `X_CONSUMER_SECRET`
- `X_ACCESS_TOKEN`
- `X_ACCESS_TOKEN_SECRET`
- `X_CLIENT_ID`
- `X_CLIENT_SECRET`
- `X_REDIRECT_URL`

These should be stored in the project’s `.env` file.

## Project Structure

Key apps and modules include:

- `accounts` — custom users, registration, profile management
- `core` — shared pages and home routing logic
- `products` — product models, views, APIs, reviews
- `stores` — store models, views, APIs
- `orders` — cart, checkout, order handling, invoice email flow
- `integrations` — external service integration logic, including X/Twitter
- `ecommerce_project` — project settings and URL configuration

## Important Files

- `manage.py` — Django management entry point
- `requirements.txt` — project dependencies
- `ecommerce_project/settings.py` — settings, database config, REST config, email config, environment variables
- `ecommerce_project/urls.py` — root URL routing
- `integrations/twitter.py` — X/Twitter posting helpers

## Requirements

This project uses Python and Django with several additional packages, including:

- Django
- djangorestframework
- djangorestframework_simplejwt
- tweepy
- python-dotenv
- requests
- PyMySQL / mariadb client support

Install dependencies with:

```bash
pip install -r requirements.txt
```

## Database Notes

The Django settings currently show a MySQL database configuration:

- database name: `ecommerce_db`
- host: `localhost`
- port: `3306`

You will need a matching database setup locally for the project to run with the current configuration.

## How to Run

1. Open a terminal.
2. Navigate to the project folder:

```bash
cd "M06T07 – Django – eCommerce Application Part 2/ecommerce_project"
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Ensure your database is configured and available.

5. Add the required environment variables to `.env`.

6. Run migrations if needed:

```bash
python manage.py migrate
```

7. Start the development server:

```bash
python manage.py runserver
```

8. Open the site in your browser.

## Typical User Flow

### Buyer Flow

1. Register as a buyer.
2. Browse active products.
3. View product details.
4. Add products to the cart.
5. Check out.
6. Receive an invoice email.
7. Leave reviews on purchased products.

### Vendor Flow

1. Register as a vendor.
2. Create a store.
3. Create products inside that store.
4. Manage existing products and store details.
5. Trigger X/Twitter announcements when stores/products are created.

## Notes

- For this cleanup pass, only **Python comments/docstrings**, **HTML comments**, and this `README.md` were intended to be updated.
- Application logic and intended behavior were left unchanged.
- Some integrations depend on valid local environment setup, especially:
  - the database,
  - email settings,
  - X/Twitter API credentials.
