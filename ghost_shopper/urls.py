from django.urls import include, path
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('', include('ghost_shopper.index_page.urls', namespace='index_page')),

    path('summernote/', include('django_summernote.urls')),

    path('core/', include('ghost_shopper.core.urls', namespace='core')),
    path('admin/', include('ghost_shopper.admin.urls', namespace='admin')),
    path('project/', include('ghost_shopper.project.urls', namespace='project')),
    path('profile/', include('ghost_shopper.auth.urls', namespace='auth')),
    path('profile/', include('ghost_shopper.user_profile.urls', namespace='profile')),
    path('check/', include('ghost_shopper.check.urls', namespace='check')),
    path('chat/', include('ghost_shopper.organisation_chat.urls', namespace='chat')),
    path('checklist/', include('ghost_shopper.checklist.urls', namespace='checklist')),
    path('organisation/', include('ghost_shopper.organisation_tree.urls', namespace='organisation')),
    path('instruction/', include('ghost_shopper.instruction.urls', namespace='instruction')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)


