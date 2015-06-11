from cms.app_base import CMSApp
from cms.apphook_pool import apphook_pool
from django.utils.translation import ugettext_lazy as _


class YolodexApp(CMSApp):
    name = _("Yolodex App")
    app_name = 'yolodex'
    urls = ["yolodex.urls"]


apphook_pool.register(YolodexApp)
