import os

import yapsy.PluginManager


def load():
    manager = yapsy.PluginManager.PluginManager()
    manager.setPluginPlaces([os.path.dirname(__file__)])
    manager.collectPlugins()
    active = [plugin.plugin_object for plugin in manager.getAllPlugins()]
    return active
