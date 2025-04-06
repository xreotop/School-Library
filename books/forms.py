from django import forms
from .models import Book

class BookForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = ['title', 'author', 'publisher', 'year', 'location', 'cover_image', 'quantity']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['publisher'].required = False
        self.fields['location'].required = False
        self.fields['cover_image'].required = False
        self.fields['year'].required = False
