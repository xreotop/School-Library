from django import forms
from .models import Book

class BookForm(forms.ModelForm):
    quantity = forms.IntegerField(min_value=1, initial=1, required=True)

    class Meta:
        model = Book
        fields = ['title', 'author', 'publisher', 'year', 'location', 'cover_image', 'isbn', 'inventory_prefix', 'fund_type']  # Добавлено fund_type
        widgets = {
            'fund_type': forms.Select()  # Используем <select> для выбора типа фонда
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['publisher'].required = False
        self.fields['location'].required = False
        self.fields['cover_image'].required = False
        self.fields['year'].required = False
        self.fields['isbn'].required = False
        self.fields['inventory_prefix'].required = True
        self.fields['fund_type'].required = True  # Тип фонда обязателен