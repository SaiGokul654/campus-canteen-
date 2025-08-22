from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from canteen.models import Category, Dish, PickupSlot
from accounts.models import UserProfile
from datetime import time

class Command(BaseCommand):
    help = 'Populate database with sample data for testing'
    
    def handle(self, *args, **options):
        self.stdout.write('Creating sample data...')
        
        # Create categories
        categories = [
            {'name': 'Main Course', 'description': 'Full meals and main dishes'},
            {'name': 'Snacks', 'description': 'Light snacks and appetizers'},
            {'name': 'Beverages', 'description': 'Drinks and beverages'},
            {'name': 'Desserts', 'description': 'Sweet treats and desserts'},
        ]
        
        for cat_data in categories:
            category, created = Category.objects.get_or_create(
                name=cat_data['name'],
                defaults={'description': cat_data['description']}
            )
            if created:
                self.stdout.write(f'Created category: {category.name}')
        
        # Create pickup slots
        pickup_slots = [
            (time(8, 0), time(9, 0)),   # 8:00 AM - 9:00 AM
            (time(12, 0), time(13, 0)), # 12:00 PM - 1:00 PM
            (time(13, 0), time(14, 0)), # 1:00 PM - 2:00 PM
            (time(17, 0), time(18, 0)), # 5:00 PM - 6:00 PM
            (time(19, 0), time(20, 0)), # 7:00 PM - 8:00 PM
        ]
        
        for start_time, end_time in pickup_slots:
            slot, created = PickupSlot.objects.get_or_create(
                start_time=start_time,
                end_time=end_time,
                defaults={'max_orders': 50}
            )
            if created:
                self.stdout.write(f'Created pickup slot: {slot}')
        
        # Create sample dishes
        main_course = Category.objects.get(name='Main Course')
        snacks = Category.objects.get(name='Snacks')
        beverages = Category.objects.get(name='Beverages')
        desserts = Category.objects.get(name='Desserts')
        
        sample_dishes = [
            # Main Course
            {
                'name': 'Chicken Biryani',
                'description': 'Aromatic basmati rice cooked with tender chicken pieces and spices',
                'category': main_course,
                'dish_type': 'non_veg',
                'price': 150.00,
                'ingredients': 'Basmati rice, chicken, onions, yogurt, spices',
                'preparation_time': 25,
                'is_featured': True,
            },
            {
                'name': 'Paneer Butter Masala',
                'description': 'Creamy tomato-based curry with soft paneer cubes',
                'category': main_course,
                'dish_type': 'veg',
                'price': 120.00,
                'ingredients': 'Paneer, tomatoes, cream, butter, spices',
                'preparation_time': 20,
                'is_featured': True,
            },
            {
                'name': 'Fish Curry Rice',
                'description': 'Traditional fish curry served with steamed rice',
                'category': main_course,
                'dish_type': 'non_veg',
                'price': 140.00,
                'ingredients': 'Fish, coconut milk, curry leaves, rice',
                'preparation_time': 30,
            },
            {
                'name': 'Dal Tadka',
                'description': 'Yellow lentils tempered with cumin and ghee',
                'category': main_course,
                'dish_type': 'veg',
                'price': 80.00,
                'ingredients': 'Yellow lentils, onions, tomatoes, spices',
                'preparation_time': 15,
            },
            
            # Snacks
            {
                'name': 'Samosa',
                'description': 'Crispy triangular pastry filled with spiced potatoes',
                'category': snacks,
                'dish_type': 'veg',
                'price': 25.00,
                'ingredients': 'Flour, potatoes, peas, spices',
                'preparation_time': 10,
            },
            {
                'name': 'Chicken Sandwich',
                'description': 'Grilled chicken sandwich with fresh vegetables',
                'category': snacks,
                'dish_type': 'non_veg',
                'price': 60.00,
                'ingredients': 'Bread, chicken, lettuce, tomatoes, mayo',
                'preparation_time': 12,
            },
            {
                'name': 'Veg Momos',
                'description': 'Steamed dumplings filled with mixed vegetables',
                'category': snacks,
                'dish_type': 'veg',
                'price': 50.00,
                'ingredients': 'Flour, cabbage, carrots, ginger, garlic',
                'preparation_time': 15,
            },
            
            # Beverages
            {
                'name': 'Masala Chai',
                'description': 'Traditional Indian spiced tea with milk',
                'category': beverages,
                'dish_type': 'beverage',
                'price': 15.00,
                'ingredients': 'Tea leaves, milk, sugar, cardamom, ginger',
                'preparation_time': 5,
            },
            {
                'name': 'Fresh Lime Soda',
                'description': 'Refreshing lime juice with soda water',
                'category': beverages,
                'dish_type': 'beverage',
                'price': 25.00,
                'ingredients': 'Fresh lime, soda water, salt, sugar',
                'preparation_time': 3,
            },
            {
                'name': 'Mango Lassi',
                'description': 'Creamy yogurt drink with fresh mango',
                'category': beverages,
                'dish_type': 'beverage',
                'price': 35.00,
                'ingredients': 'Yogurt, mango, sugar, cardamom',
                'preparation_time': 5,
            },
            
            # Desserts
            {
                'name': 'Gulab Jamun',
                'description': 'Soft milk solids dumplings in sugar syrup',
                'category': desserts,
                'dish_type': 'veg',
                'price': 40.00,
                'ingredients': 'Milk powder, flour, sugar, cardamom',
                'preparation_time': 20,
            },
            {
                'name': 'Ice Cream',
                'description': 'Vanilla ice cream with chocolate sauce',
                'category': desserts,
                'dish_type': 'veg',
                'price': 30.00,
                'ingredients': 'Milk, cream, vanilla, chocolate',
                'preparation_time': 2,
            },
        ]
        
        for dish_data in sample_dishes:
            dish, created = Dish.objects.get_or_create(
                name=dish_data['name'],
                defaults=dish_data
            )
            if created:
                self.stdout.write(f'Created dish: {dish.name}')
        
        # Create sample users
        if not User.objects.filter(username='admin').exists():
            admin_user = User.objects.create_user(
                username='admin',
                email='admin@canteen.com',
                password='admin123',
                first_name='Admin',
                last_name='User'
            )
            UserProfile.objects.create(
                user=admin_user,
                role='admin',
                phone='9876543210'
            )
            self.stdout.write('Created admin user (username: admin, password: admin123)')
        
        if not User.objects.filter(username='staff').exists():
            staff_user = User.objects.create_user(
                username='staff',
                email='staff@canteen.com',
                password='staff123',
                first_name='Staff',
                last_name='Member'
            )
            UserProfile.objects.create(
                user=staff_user,
                role='staff',
                phone='9876543211'
            )
            self.stdout.write('Created staff user (username: staff, password: staff123)')
        
        if not User.objects.filter(username='student').exists():
            student_user = User.objects.create_user(
                username='student',
                email='student@college.edu',
                password='student123',
                first_name='John',
                last_name='Doe'
            )
            UserProfile.objects.create(
                user=student_user,
                role='student',
                student_id='ST001',
                phone='9876543212'
            )
            self.stdout.write('Created student user (username: student, password: student123)')
        
        self.stdout.write(self.style.SUCCESS('Sample data created successfully!'))
        self.stdout.write(self.style.SUCCESS('You can now login with:'))
        self.stdout.write('Admin: admin/admin123')
        self.stdout.write('Staff: staff/staff123') 
        self.stdout.write('Student: student/student123')