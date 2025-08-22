from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Avg
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from datetime import datetime, date, timedelta
from .models import Dish, Category, Review, PreOrder, PickupSlot
from .forms import ReviewForm, PreOrderForm
from accounts.models import UserProfile

def menu(request):
    """Display the daily menu with search and filter options"""
    dishes = Dish.objects.filter(is_available=True).select_related('category')
    categories = Category.objects.filter(is_active=True)
    
    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        dishes = dishes.filter(
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(ingredients__icontains=search_query)
        )
    
    # Filter by category
    category_filter = request.GET.get('category', '')
    if category_filter:
        dishes = dishes.filter(category__id=category_filter)
    
    # Filter by dish type
    dish_type_filter = request.GET.get('dish_type', '')
    if dish_type_filter:
        dishes = dishes.filter(dish_type=dish_type_filter)
    
    # Sort options
    sort_by = request.GET.get('sort', 'name')
    if sort_by == 'price':
        dishes = dishes.order_by('price')
    elif sort_by == 'rating':
        dishes = dishes.annotate(avg_rating=Avg('review__rating')).order_by('-avg_rating')
    else:
        dishes = dishes.order_by('name')
    
    # Pagination
    paginator = Paginator(dishes, 12)  # 12 dishes per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'categories': categories,
        'search_query': search_query,
        'category_filter': category_filter,
        'dish_type_filter': dish_type_filter,
        'sort_by': sort_by,
    }
    return render(request, 'canteen/menu.html', context)

def dish_detail(request, pk):
    """Display dish details with reviews and pre-order option"""
    dish = get_object_or_404(Dish, pk=pk)
    reviews = Review.objects.filter(dish=dish).select_related('user')
    user_review = None
    
    if request.user.is_authenticated:
        try:
            user_review = Review.objects.get(dish=dish, user=request.user)
        except Review.DoesNotExist:
            pass
    
    # Handle review submission
    if request.method == 'POST' and request.user.is_authenticated:
        if 'review_submit' in request.POST:
            review_form = ReviewForm(request.POST)
            if review_form.is_valid():
                review, created = Review.objects.get_or_create(
                    dish=dish,
                    user=request.user,
                    defaults={
                        'rating': review_form.cleaned_data['rating'],
                        'comment': review_form.cleaned_data['comment']
                    }
                )
                if not created:
                    review.rating = review_form.cleaned_data['rating']
                    review.comment = review_form.cleaned_data['comment']
                    review.save()
                
                messages.success(request, 'Review submitted successfully!')
                return redirect('canteen:dish_detail', pk=pk)
    
    review_form = ReviewForm()
    if user_review:
        review_form = ReviewForm(instance=user_review)
    
    context = {
        'dish': dish,
        'reviews': reviews,
        'user_review': user_review,
        'review_form': review_form,
    }
    return render(request, 'canteen/dish_detail.html', context)

@login_required
def prebook_dish(request, dish_id):
    """Pre-book a dish for pickup"""
    dish = get_object_or_404(Dish, id=dish_id, is_available=True)
    pickup_slots = PickupSlot.objects.filter(is_active=True)
    
    if request.method == 'POST':
        form = PreOrderForm(request.POST)
        if form.is_valid():
            preorder = form.save(commit=False)
            preorder.user = request.user
            preorder.dish = dish
            preorder.save()
            
            messages.success(request, f'Pre-order placed successfully! Order number: {preorder.order_number}')
            return redirect('canteen:dashboard')
    else:
        form = PreOrderForm()
        # Set default date to tomorrow
        form.fields['date'].initial = date.today() + timedelta(days=1)
    
    context = {
        'dish': dish,
        'form': form,
        'pickup_slots': pickup_slots,
    }
    return render(request, 'canteen/prebook.html', context)

@login_required
def dashboard(request):
    """Student dashboard showing their preorders"""
    preorders = PreOrder.objects.filter(user=request.user).select_related('dish', 'pickup_slot')
    
    # Filter by status
    status_filter = request.GET.get('status', '')
    if status_filter:
        preorders = preorders.filter(status=status_filter)
    
    # Separate into categories
    pending_orders = preorders.filter(status='pending')
    confirmed_orders = preorders.filter(status='confirmed')
    ready_orders = preorders.filter(status='ready')
    picked_orders = preorders.filter(status='picked')
    
    context = {
        'preorders': preorders,
        'pending_orders': pending_orders,
        'confirmed_orders': confirmed_orders,
        'ready_orders': ready_orders,
        'picked_orders': picked_orders,
        'status_filter': status_filter,
    }
    return render(request, 'canteen/dashboard.html', context)

@login_required
@require_POST
def cancel_preorder(request, order_id):
    """Cancel a preorder"""
    preorder = get_object_or_404(PreOrder, id=order_id, user=request.user)
    
    if preorder.status in ['pending', 'confirmed']:
        preorder.status = 'cancelled'
        preorder.save()
        messages.success(request, 'Order cancelled successfully!')
    else:
        messages.error(request, 'Cannot cancel this order.')
    
    return redirect('canteen:dashboard')

# Staff/Admin Views
@login_required
def manage_dishes(request):
    """Staff view to manage dishes and availability"""
    # Check if user is staff
    try:
        profile = UserProfile.objects.get(user=request.user)
        if not profile.is_staff_member:
            messages.error(request, 'Access denied. Staff only.')
            return redirect('canteen:menu')
    except UserProfile.DoesNotExist:
        messages.error(request, 'Access denied.')
        return redirect('canteen:menu')
    
    dishes = Dish.objects.all().select_related('category')
    
    # Handle availability toggle
    if request.method == 'POST':
        dish_id = request.POST.get('dish_id')
        action = request.POST.get('action')
        
        if dish_id and action:
            dish = get_object_or_404(Dish, id=dish_id)
            if action == 'toggle_availability':
                dish.is_available = not dish.is_available
                dish.save()
                status = "available" if dish.is_available else "sold out"
                messages.success(request, f'{dish.name} marked as {status}')
    
    context = {
        'dishes': dishes,
    }
    return render(request, 'canteen/admin/manage_dishes.html', context)

@login_required
def manage_preorders(request):
    """Staff view to manage preorders"""
    # Check if user is staff
    try:
        profile = UserProfile.objects.get(user=request.user)
        if not profile.is_staff_member:
            messages.error(request, 'Access denied. Staff only.')
            return redirect('canteen:menu')
    except UserProfile.DoesNotExist:
        messages.error(request, 'Access denied.')
        return redirect('canteen:menu')
    
    preorders = PreOrder.objects.all().select_related('user', 'dish', 'pickup_slot')
    
    # Filter by date
    date_filter = request.GET.get('date', '')
    if date_filter:
        preorders = preorders.filter(date=date_filter)
    else:
        # Default to today's orders
        preorders = preorders.filter(date=date.today())
    
    # Filter by status
    status_filter = request.GET.get('status', '')
    if status_filter:
        preorders = preorders.filter(status=status_filter)
    
    # Handle status updates
    if request.method == 'POST':
        order_id = request.POST.get('order_id')
        new_status = request.POST.get('status')
        
        if order_id and new_status:
            preorder = get_object_or_404(PreOrder, id=order_id)
            preorder.status = new_status
            preorder.save()
            messages.success(request, f'Order #{preorder.order_number} status updated to {new_status}')
    
    context = {
        'preorders': preorders,
        'date_filter': date_filter,
        'status_filter': status_filter,
        'today': date.today(),
    }
    return render(request, 'canteen/admin/manage_preorders.html', context)