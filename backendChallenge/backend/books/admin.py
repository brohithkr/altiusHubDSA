from django.contrib import admin
from .models import Book


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'isbn', 'publication_date', 'price', 'created_at']
    list_filter = ['author', 'publication_date', 'created_at']
    search_fields = ['title', 'author', 'isbn', 'description']
    readonly_fields = ['created_at', 'updated_at']
    fieldsets = (
        ('Book Information', {
            'fields': ('title', 'author', 'isbn', 'publication_date', 'pages', 'price')
        }),
        ('Additional Information', {
            'fields': ('description', 'created_by')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
