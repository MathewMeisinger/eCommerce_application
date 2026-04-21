from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, HttpResponseBadRequest
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.urls import reverse_lazy
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.conf import settings
from .models import Cart, CartItem, Order, OrderItem
from products.models import Product


def get_or_create_cart(user):
    """
    Return the current cart for a user, creating one if needed.
    """
    cart, _ = Cart.objects.get_or_create(user=user)

    return cart


@login_required
def add_to_cart(request, product_id):
    """
    Accepts a POST request and adds a product to the user's cart.
    """

    if request.method != 'POST':
        return HttpResponseBadRequest('POST REQUIRED')

    qty = int(request.POST.get('quantity', 1))

    product = get_object_or_404(Product, pk=product_id)

    cart = get_or_create_cart(request.user)

    item, created = CartItem.objects.get_or_create(
        cart=cart,
        product=product
    )

    if not created:
        item.quantity += qty
    else:
        item.quantity = qty

    item.save()

    # Return JSON when the request came from asynchronous JavaScript.
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({
            'status': 'ok',
            'cart_count': cart.items.count(),
            'item_quantity': item.quantity,
        })

    return redirect('cart-detail')


@login_required
def cart_detail(request):
    """Display the current user's cart contents and total price."""
    cart = get_or_create_cart(request.user)
    items = cart.items.select_related('product').all()
    total = cart.total_price()
    return render(request, 'orders/cart_detail.html', {'cart': cart, 'items': items, 'total': total})


@login_required
def update_cart_item(request, pk):
    """Update the quantity of a cart item or remove it entirely."""
    item = get_object_or_404(CartItem, pk=pk, cart__user=request.user)

    if request.method != 'POST':
        return HttpResponseBadRequest('POST REQUIRED')

    action = request.POST.get('action')
    if action == 'remove':
        item.delete()
    else:
        qty = int(request.POST.get('quantity', 1))
        if qty <= 0:
            item.delete()
        else:
            item.quantity = qty
            item.save()
    return redirect('cart-detail')


@login_required
def checkout(request):
    """
    Process checkout, create the order, update stock, and send an invoice.
    """
    cart = get_or_create_cart(request.user)
    cart_items = cart.items.select_related('product').all()
    if not cart_items:
        return redirect('cart-detail')

    # Process the checkout only after the buyer confirms the order.
    if request.method == 'POST':
        # Run checkout inside a transaction so stock and order data stay aligned.
        with transaction.atomic():
            product_ids = [ci.product.pk for ci in cart_items]
            products = Product.objects.select_for_update().filter(pk__in=product_ids)
            products_map = {p.pk: p for p in products}

            # Confirm that each requested item still has enough stock available.
            for ci in cart_items:
                p = products_map.get(ci.product.pk)
                if p is None:
                    raise ValueError("Product disappeared")
                if ci.quantity > p.stock:
                    # Re-render the cart with an error if stock is insufficient.
                    context = {
                        'cart': cart,
                        'items': cart_items,
                        'error': f"Not enough stock for {p.name}. Available: {p.stock}"
                    }
                    return render(request, 'orders/cart_detail.html', context)

            # Calculate the full order total from the current cart contents.
            total = sum(ci.product.price * ci.quantity for ci in cart_items)

            # Create the order header first.
            order = Order.objects.create(user=request.user, total_price=total)

            # Create order lines and reduce stock for each purchased product.
            for ci in cart_items:
                p = products_map[ci.product.pk]
                OrderItem.objects.create(
                    order=order,
                    product=p,
                    quantity=ci.quantity,
                    price_each=p.price
                )
                # Reduce the available stock after purchase.
                p.stock = p.stock - ci.quantity
                p.save()

            # Send the invoice email once the order has been created.
            send_order_invoice_email(order)

            # Clear the cart after a successful checkout.
            cart.items.all().delete()

        return redirect('order-success', order_id=order.pk)

    # Show the checkout confirmation page for GET requests.
    total = cart.total_price()
    return render(request, 'orders/checkout.html', {'cart': cart, 'items': cart_items, 'total': total})


@login_required
def order_success(request, order_id):
    """Display the success page for a completed order."""
    order = get_object_or_404(Order, pk=order_id, user=request.user)
    return render(request, 'orders/order_success.html', {'order':order})


def send_order_invoice_email(order):
    """Generate and send a plain-text invoice email for an order."""
    subject = f'Invoice for order #{order.pk}'
    to_email = [order.user.email]
    context = {'order': order, 'items': order.items.all(), 'user': order.user}

    # Render the plain-text invoice body from the email template.
    message_text = render_to_string('orders/email/order_invoice.txt', context)

    email = EmailMessage(subject=subject, body=message_text, to=to_email)
    email.content_subtype = 'plain'
    email.send(fail_silently=False)

    # Mark the order so the system knows the invoice email was sent.
    order.email_sent = True
    order.save()
