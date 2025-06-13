from django import forms
from .models import Book

class BookForm(forms.ModelForm):
    quantity = forms.IntegerField(min_value=1, initial=1, required=True)

    class Meta:
        model = Book
        fields = [
            'title', 'author', 'publisher', 'year', 'location', 'cover_image',
            'isbn', 'inventory_prefix', 'batch_number', 'inventory_digit', 'fund_type',
            'acquisition_date', 'acquisition_source', 'acquisition_price'
        ]
        widgets = {
            'fund_type': forms.Select(),
            'acquisition_date': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['publisher'].required = False
        self.fields['location'].required = False
        self.fields['cover_image'].required = False
        self.fields['year'].required = False
        self.fields['isbn'].required = False
        self.fields['inventory_prefix'].required = True
        self.fields['batch_number'].required = False
        self.fields['inventory_digit'].required = False  # Заменили inventory_number на inventory_digit
        self.fields['fund_type'].required = True
        self.fields['acquisition_date'].required = False
        self.fields['acquisition_source'].required = False
        self.fields['acquisition_price'].required = False
