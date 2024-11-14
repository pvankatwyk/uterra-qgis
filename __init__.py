
def classFactory(iface):
    from .uterra_plugin import Uterra
    return Uterra(iface)