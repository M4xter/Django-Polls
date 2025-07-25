from django.contrib import admin
from .models import Choice, Question, Restaurant

class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 3

class RestaurantAdmin(admin.ModelAdmin):
    list_display = ('name', 'type', 'address', 'description') 

class QuestionAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {"fields": ["question_text"]}),
        ("Date information", {"fields": ["pub_date"], "classes": ["collapse"]}),
    ]
    inlines = [ChoiceInline]
    list_display = ["question_text", "pub_date", "was_published_recently"]
    list_filter = ["pub_date"]
    search_fields = ["question_text"]

admin.site.register(Restaurant)
admin.site.register(Choice)
admin.site.register(Question, QuestionAdmin)