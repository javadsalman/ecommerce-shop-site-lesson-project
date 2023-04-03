from django.test import TestCase, override_settings
from .models import Category, Product, Review
from .forms import ReviewForm
from customer.models import Customer
from django.contrib.auth.models import User

# Create your tests here.
class CategoryTest(TestCase):
    def setUp(self):
        self.c1 = Category.objects.create(image='path/', title='Ust geyim')
        self.c2 = Category.objects.create(super=self.c1, image='path/', title='Koynekler')

    def test_is_super(self):
        self.assertTrue(self.c1.is_super())
        self.assertFalse(self.c2.is_super())
        
    def test_absolute_url(self):
        url = self.c1.get_absolute_url()
        pk = self.c1.pk
        self.assertEqual(url, f'/en/products/?category={pk}')
    
    
class ProductTest(TestCase):

    def setUp(self):
        self.product = Product.objects.create(
            title_az='qəhvəyi pencək',
            title_en='brown jacket',
            title_tr='kahve renkli ceket',
            description='bir jaket novu',
            price=12.5
        )
        
    @override_settings(LANGUAGE_CODE='en')
    def test_en_title(self):
        self.assertEqual(self.product.title, 'brown jacket')
        
    @override_settings(LANGUAGE_CODE='az')
    def test_az_title(self):
        self.assertEqual(self.product.title, 'qəhvəyi pencək')
        
    @override_settings(LANGUAGE_CODE='tr')
    def test_tr_title(self):
        self.assertEqual(self.product.title, 'kahve renkli ceket')

    def test_slug(self):
        self.assertEqual(self.product.slug, 'qehveyi-pencek')
        

class ReviewTest(TestCase):
    
    def setUp(self):
        self.user = User.objects.create_user('eli', 'eli@gmail.com', 'eli123')
        self.customer = self.user.customer
        self.product = Product.objects.create(
            title_az='qəhvəyi pencək',
            title_en='brown jacket',
            title_tr='kahve renkli ceket',
            description='bir jaket novu',
            price=12.5
        )
        
    def test_review_form(self):
        form = ReviewForm({'star_count': 4, 'comment': 'Ela idi!'})
        validity = form.is_valid()
        self.assertTrue(validity)
        
        form = ReviewForm({'star_count': 7, 'comment': 'Ela idi!'})
        validity = form.is_valid()
        self.assertFalse(validity)
        
        form = ReviewForm({'star_count': 6, 'comment': 'Ela idi!'})
        validity = form.is_valid()
        self.assertFalse(validity)

        form = ReviewForm({'star_count': 5, 'comment': ''})
        validity = form.is_valid()
        self.assertFalse(validity, 'Bos comment olanda False olmalidi!')