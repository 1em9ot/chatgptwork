import os
import importlib.util
import logging

class PluginManager:
    def __init__(self):
        self.plugins = {}
        logging.debug("PluginManager initialized")

    def register_plugin(self, name: str, plugin):
        self.plugins[name] = plugin
        logging.info(f"Plugin registered: {name}")

    def get_plugin(self, name: str):
        plugin = self.plugins.get(name)
        if plugin:
            logging.debug(f"Plugin {name} retrieved")
        else:
            logging.warning(f"Plugin {name} not found")
        return plugin

    def load_plugins_from_directory(self, directory: str, file_suffix: str = "_plugin.py"):
        logging.info(f"Loading plugins from directory: {directory}")
        try:
            for filename in os.listdir(directory):
                if filename.endswith(file_suffix):
                    filepath = os.path.join(directory, filename)
                    module_name = os.path.splitext(filename)[0]
                    spec = importlib.util.spec_from_file_location(module_name, filepath)
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)
                    plugin_name = getattr(module, "PLUGIN_NAME", module_name)
                    self.register_plugin(plugin_name, module)
            logging.info(f"Total plugins loaded: {len(self.plugins)}")
        except Exception as e:
            logging.error(f"Failed to load plugins from {directory}: {e}")
