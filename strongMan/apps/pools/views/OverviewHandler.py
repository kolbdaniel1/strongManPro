from django.contrib import messages
from django.shortcuts import render
from django_tables2 import RequestConfig
from strongMan.apps.pools.models import Pool
from strongMan.helper_apps.vici.wrapper.exception import ViciException
from .. import tables
from django.template.loader import render_to_string
from strongMan.helper_apps.vici.wrapper.wrapper import ViciWrapper


class OverviewHandler:
    def __init__(self, request):
        self.request = request
        self.ENTRIES_PER_PAGE = 50

    def handle(self):
        try:
            return self._render()
        except ViciException as e:
            messages.warning(self.request, str(e))

    def _render(self):
        queryset = Pool.objects.all()
        table = tables.PoolsTable(queryset, request=self.request)

        # pools = ViciWrapper().get_pools()

        RequestConfig(self.request, paginate={"per_page": self.ENTRIES_PER_PAGE}).configure(table)
        if len(queryset) == 0:
            table = None
        return render(self.request, 'pools/overview.html', {'table': table})
        # return render(self.request, 'pools/overview.html', {'table': table, 'pools': pools})

#     def handle_collapse(self, record):
#         pools = ViciWrapper().get_pools()
#         pool_details = {k: v for k, v in pools.items() if str(k) == str(record)}
#         size = 0
#         base = None
#         online = 0
#         offline = 0
#         leases = None
#
#         for key, value in pool_details[str(record)].items():
#             if key == 'size':
#                 size = value
#             elif key == 'base':
#                 base = value
#             elif key == 'online':
#                 online = value
#             elif key == 'offline':
#                 offline = value
#             elif key == 'leases':
#                 leases = value
#         return {'record': record, 'detail': pool_details, 'size': size, 'base': base,
#                                                                               'online': online, 'offline': offline,
#                                                                               'leases': leases}
#

    def handle_collapse(self, record):
        pools = ViciWrapper().get_pools()
        pool_details = {k: v for k, v in pools.items() if str(k) == str(record)}
        size = 0
        base = None
        online = 0
        offline = 0
        leases = None

        for key, value in pool_details[str(record)].items():
            if key == 'size':
                size = value
            elif key == 'base':
                base = value
            elif key == 'online':
                online = value
            elif key == 'offline':
                offline = value
            elif key == 'leases':
                leases = value
        return render_to_string('pools/overview.html', {'record': record, 'detail': pool_details,
                                                        'size': size, 'base': base,
                                                        'online': online, 'offline': offline,
                                                        'leases': leases},
                                request=self.request)
