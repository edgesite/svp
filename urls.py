from django.conf.urls.defaults import *

urlpatterns = patterns('realtest.data.views',
     (r'^$', 'index'),
     (r'^changes/$', 'changes'),
     (r'^contacts/$', 'contacts'),
     (r'^edits/(?P<Barcode_No>\d+)/$', 'edits'),
     (r'^match/(?P<Barcode_No>\d+)/$', 'match'),
     (r'^preferences/$', 'preferences'),
     (r'^results/$', 'results'),
     (r'^saved/$', 'saved'),
     (r'^show/(?P<Barcode_No>\d+)/$', 'show'),
     (r'^test/$', 'test'),
     (r'^tmp/migrated/$', 'show'),
     (r'^upload/$', 'upload'),
)
