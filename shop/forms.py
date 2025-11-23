from django import forms
from .models import Order, Review
from django.forms.widgets import RadioSelect # Import RadioSelect

class OrderCreateForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['first_name', 'last_name', 'email', 'address',
                  'celular', 'notes']

class ReviewForm(forms.ModelForm):
    rating = forms.ChoiceField(
        choices=[(i, str(i)) for i in range(1, 6)], # Choices 1 to 5
        widget=RadioSelect,
        label="Tu Calificación"
    )
    class Meta:
        model = Review
        fields = ['rating', 'comment']
        widgets = {
            'comment': forms.Textarea(attrs={'rows': 4}),
        }
