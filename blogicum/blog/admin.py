from django.contrib import admin

from blog.models import Category
from blog.models import Location
from blog.models import Post
from blog.models import Comment


class CommentsInLine(admin.StackedInline):
    model = Comment
    extra = 0


class PostAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'pub_date',
        'author',
        'location',
        'category',
        'is_published',
        'created_at',
    )
    list_editable = (
        'pub_date',
        'is_published'
    )
    inlines = (CommentsInLine,)
    search_fields = ('title',)
    list_filter = ('category',)
    list_display_links = ('title',)
    empty_value_display = 'Не задано'


class PostsInLine(admin.StackedInline):
    model = Post
    extra = 0


class CategoryAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'slug',
        'is_published',
        'created_at',
    )
    list_editable = ('is_published',)
    inlines = (PostsInLine,)


class CommentAdmin(admin.ModelAdmin):
    list_display = (
        'author',
        'text',
        'created_at',
    )


admin.site.register(Category, CategoryAdmin)
admin.site.register(Location)
admin.site.register(Post, PostAdmin)
admin.site.register(Comment, CommentAdmin)
