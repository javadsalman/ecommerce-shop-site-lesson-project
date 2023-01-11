from django import forms
from .models import Review

class ReviewForm(forms.ModelForm):
    
    class Meta:
        model = Review
        fields = ['star_count', 'comment']
        
    def save(self, customer, product):
        review = Review.objects.create(
            customer=customer,
            product=product,
            star_count=self.cleaned_data.get('star_count'),
            comment=self.cleaned_data.get('comment'),
        )
        return review