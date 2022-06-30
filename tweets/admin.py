from django.contrib import admin
from tweets.models import Tweet


@admin.register(Tweet)
class TweetAdmin(admin.ModelAdmin):
    date_hierarchy = 'created_at'
    # 在list界面展示的
    list_display = (
        'created_at',
        'user',
        'content',
    )
