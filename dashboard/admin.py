from django.contrib import admin
from .models import *



admin.site.register(Profile)
admin.site.register(Blog)
admin.site.register(BlogSection)
admin.site.register(UserMembership)
admin.site.register(Membership)
admin.site.register(Subscription)
# admin.site.register(StripeCustomer)
admin.site.register(StripeSubscription)
admin.site.register(Content)
admin.site.register(ContentSection)
admin.site.register(StudyNote)
admin.site.register(ChatMessages)
admin.site.register(OpenaiMessages)
admin.site.register(GeneratedProductName)
admin.site.register(GeneratedRecipe)







