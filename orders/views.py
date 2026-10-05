from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST

from .forms import ContactForm, LoginForm, OrderForm, RegisterForm
from .models import Order


def _safe_next(request, fallback='home'):
    """Return the ?next= target if it points at this site, otherwise the fallback."""
    target = request.POST.get('next') or request.GET.get('next')
    if target and url_has_allowed_host_and_scheme(target, allowed_hosts={request.get_host()},
                                                  require_https=request.is_secure()):
        return target
    return fallback


def home(request):
    return render(request, 'orders/home.html')


def product(request):
    return render(request, 'orders/product.html')


def contact(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Thanks for reaching out! We'll get back to you within 24 hours.")
            return redirect('contact')
    else:
        initial = {}
        if request.user.is_authenticated:
            initial = {'name': request.user.get_full_name() or request.user.username,
                       'email': request.user.email}
        form = ContactForm(initial=initial)
    return render(request, 'orders/contact.html', {'form': form})


def register_user(request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f"Welcome, {user.username}! Your account has been created.")
            return redirect(_safe_next(request))
    else:
        form = RegisterForm()
    return render(request, 'orders/register.html', {'form': form, 'next': _safe_next(request, '')})


def login_user(request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            login(request, form.get_user())
            if not request.POST.get('remember'):
                request.session.set_expiry(0)  # expire when the browser closes
            messages.success(request, 'You have been logged in.')
            return redirect(_safe_next(request))
        messages.error(request, 'Invalid username or password. Please try again.')
    else:
        form = LoginForm(request)
    return render(request, 'orders/login.html', {'form': form, 'next': _safe_next(request, '')})


@require_POST
def logout_user(request):
    logout(request)
    messages.info(request, 'You have logged out.')
    return redirect('login')


@login_required
def order_now(request):
    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            order.user = request.user
            order.save()
            return redirect('order_success', pk=order.pk)
    else:
        initial = {}
        if request.GET.get('product') in dict(Order.PRODUCT_CHOICES):
            initial['product'] = request.GET['product']
        # Prefill delivery details from the customer's most recent order.
        last = request.user.orders.first()
        if last:
            initial.update(location=last.location, delivery_address=last.delivery_address, phone=last.phone)
        form = OrderForm(initial=initial)
    return render(request, 'orders/order_now.html', {'form': form})


@login_required
def order_success(request, pk):
    order = get_object_or_404(Order, pk=pk, user=request.user)
    return render(request, 'orders/order_success.html', {'order': order})


@login_required
def my_orders(request):
    return render(request, 'orders/my_orders.html', {'orders': request.user.orders.all()})


@login_required
@require_POST
def cancel_order(request, pk):
    order = get_object_or_404(Order, pk=pk, user=request.user)
    if order.can_cancel:
        order.status = 'cancelled'
        order.save(update_fields=['status'])
        messages.info(request, f'Order #{order.pk} has been cancelled.')
    else:
        messages.error(request, f'Order #{order.pk} can no longer be cancelled.')
    return redirect('my_orders')
