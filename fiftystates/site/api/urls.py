from django.conf import settings
from django.conf.urls.defaults import *

import piston.resource
from piston.emitters import Emitter

from fiftystates.site.api.handlers import *
from fiftystates.site.api.views import document
from fiftystates.site.api.models import LogEntry

if getattr(settings, 'USE_LOCKSMITH', False):
    from locksmith.auth.authentication import PistonKeyAuthentication
    authorizer = PistonKeyAuthentication()

    class Resource(piston.resource.Resource):
        def __call__(self, request, *args, **kwargs):
            resp = super(Resource, self).__call__(request, *args, **kwargs)

            try:
                LogEntry.objects.create(
                    caller_key=request.apikey.key,
                    method=self.handler.__class__.__name__,
                    query_string=request.META['QUERY_STRING'],
                )
            except AttributeError:
                pass

            return resp
else:
    authorizer = None
    Resource = piston.resource.Resource

Emitter.unregister('xml')

metadata_handler = Resource(MetadataHandler, authentication=authorizer)
bill_handler = Resource(BillHandler, authentication=authorizer)
bill_search_handler = Resource(BillSearchHandler, authentication=authorizer)
legislator_handler = Resource(LegislatorHandler, authentication=authorizer)
legsearch_handler = Resource(LegislatorSearchHandler,
                             authentication=authorizer)
legislator_geo_handler = Resource(LegislatorGeoHandler,
                                  authentication=authorizer)
committee_handler = Resource(CommitteeHandler, authentication=authorizer)
committee_search_handler = Resource(CommitteeSearchHandler,
                                    authentication=authorizer)
stats_handler = Resource(StatsHandler, authentication=authorizer)

urlpatterns = patterns('',
    # v1 urls
    url(r'^v1/metadata/(?P<state>[a-zA-Z]{2,2})/$', metadata_handler),

    # two urls for bill handler
    url(r'^v1/bills/(?P<state>[a-zA-Z]{2,2})/(?P<session>.+)/'
        r'(?P<chamber>upper|lower)/(?P<bill_id>.+)/$', bill_handler),
    url(r'^v1/bills/(?P<state>[a-zA-Z]{2,2})/(?P<session>.+)/'
        r'(?P<bill_id>.+)/$', bill_handler),
    url(r'^v1/bills/$', bill_search_handler),

    url(r'^v1/legislators/(?P<id>[A-Z]{2,2}L\d{6,6})/$', legislator_handler),
    url(r'^v1/legislators/$', legsearch_handler),
    url(r'^v1/legislators/geo/$', legislator_geo_handler),

    url(r'^v1/committees/(?P<id>[A-Z]{2,2}C\d{6,6})/$', committee_handler),
    url(r'^v1/committees/$', committee_search_handler),

    url(r'^v1/documents/(?P<id>[A-Z]{2,2}D\d{8,8})/$', document),

    url(r'^v1/stats/$', stats_handler),
)
