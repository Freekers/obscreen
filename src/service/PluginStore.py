import os
import logging
import inspect
import importlib

from src.interface.ObPlugin import ObPlugin
from src.interface.ObController import ObController
from src.constant.WebDirConstant import WebDirConstant
from src.service.ModelStore import ModelStore
from src.service.WebServer import WebServer
from src.service.TemplateRenderer import TemplateRenderer
from src.manager.VariableManager import VariableManager
from src.model.enum.VariableType import VariableType
from src.model.enum.HookType import HookType
from src.model.hook.HookRegistration import HookRegistration
from src.model.hook.StaticHookRegistration import StaticHookRegistration
from typing import List, Dict, Union


class PluginStore:

    FOLDER_PLUGINS_SYSTEM = 'plugins/system'
    FOLDER_PLUGINS_USER = 'plugins/user'
    DEFAULT_PLUGIN_ENABLED_VARIABLE = "enabled"

    def __init__(self, project_dir: str, model_store: ModelStore, template_renderer: TemplateRenderer, web_server: WebServer):
        self._project_dir = project_dir
        self._model_store = model_store
        self._template_renderer = template_renderer
        self._web_server = web_server
        self._hooks = self.pre_load_hooks()
        self._dead_variables_candidates = VariableManager.list_to_map(self._model_store.variable().get_by_prefix(ObPlugin.PLUGIN_PREFIX))
        self._system_plugins = self.find_plugins_in_directory(self.FOLDER_PLUGINS_SYSTEM)
        self._system_plugins = self.find_plugins_in_directory(self.FOLDER_PLUGINS_USER)
        self.post_load_hooks()
        self.clean_dead_variables()


    def map_hooks(self) -> Dict[HookType, List[HookRegistration]]:
        return self._hooks

    def find_plugins_in_directory(self, directory: str) -> list:
        plugins = []
        for root, dirs, files in os.walk('{}/{}'.format(self._project_dir, directory)):
            for file in files:
                if file.endswith(".py"):
                    module_name = file[:-3]
                    module_path = os.path.join(root, file)
                    spec = importlib.util.spec_from_file_location(module_name, module_path)
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)
                    for name, obj in inspect.getmembers(module):
                        if inspect.isclass(obj) and issubclass(obj, ObPlugin) and obj is not ObPlugin:
                            plugin = obj(
                                project_dir=self._project_dir,
                                plugin_dir=root,
                                model_store=self._model_store,
                                template_renderer=self._template_renderer
                            )
                            plugins.append(plugin)
                            self.setup_plugin(plugin)

        return plugins

    def load_controllers(self, plugin: ObPlugin) -> None:
        for root, dirs, files in os.walk("{}/{}".format(plugin.get_directory(), WebDirConstant.FOLDER_CONTROLLER)):
            for file in files:
                if file.endswith(".py"):
                    module_name = file[:-3]
                    module_path = os.path.join(root, file)
                    spec = importlib.util.spec_from_file_location(module_name, module_path)
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)
                    for name, obj in inspect.getmembers(module):
                        if inspect.isclass(obj) and issubclass(obj, ObController) and obj is not ObController:
                            obj(
                                app=self._web_server.get_app(),
                                model_store=self._model_store,
                                template_renderer=self._template_renderer,
                                plugin=plugin
                            )

                            logging.info("[plugin:{}] Controller {} loaded".format(
                                plugin.use_id(),
                                obj.__name__
                            ))

    def pre_load_hooks(self) -> Dict[HookType, List[HookRegistration]]:
        hooks = {}

        for hook in HookType:
            hooks[hook] = []

        return hooks

    def post_load_hooks(self) -> None:
        for hook_type in self._hooks:
            self._hooks[hook_type] = sorted(self._hooks[hook_type], key=lambda hook_reg: hook_reg.priority, reverse=True)

    def setup_plugin(self, plugin: ObPlugin) -> None:
        # VARIABLES
        variables = plugin.use_variables() + [
            plugin.add_variable(
                name=self.DEFAULT_PLUGIN_ENABLED_VARIABLE,
                value=False,
                type=VariableType.BOOL,
                editable=True,
                description="Enable {} plugin".format(plugin.use_title())
            )
        ]

        for variable in variables:
            if variable.name in self._dead_variables_candidates:
                del self._dead_variables_candidates[variable.name]

        if not self.is_plugin_enabled(plugin):
            return

        # HOOKS
        hooks_registrations = plugin.use_hooks_registrations()

        for hook_registration in hooks_registrations:
            if hook_registration.hook not in self._hooks:
                logging.error("[plugin:{}] Hook {} does not exist".format(plugin.use_id(), hook.name))
                continue

            if isinstance(hook_registration, StaticHookRegistration):
                hook_registration.template = "{}/views/{}.jinja.html".format(plugin.get_directory(), hook_registration.hook.value)

            self._hooks[hook_registration.hook].append(hook_registration)

        logging.info("[plugin:{}] {} variable{} loaded".format(
            plugin.use_id(),
            len(variables),
            "s" if len(variables) > 1 else "",
        ))

        logging.info("[plugin:{}] {} hook{} loaded".format(
            plugin.use_id(),
            len(hooks_registrations),
            "s" if len(hooks_registrations) > 1 else "",
        ))

        # LANGS
        self._model_store.lang().load(directory=plugin.get_directory(), prefix=plugin.use_id())
        self._model_store.variable().reload(lang_map=self._model_store.lang().map())

        # WEB CONTROLLERS
        self.load_controllers(plugin)


    def clean_dead_variables(self) -> None:
        for variable_name, variable in self._dead_variables_candidates.items():
            logging.info("Removing dead plugin variable {}".format(variable_name))
            self._model_store.variable().delete(variable.id)

    def is_plugin_enabled(self, plugin: ObPlugin) -> bool:
        var = self._model_store.variable().get_one_by_name(plugin.get_plugin_variable_name(self.DEFAULT_PLUGIN_ENABLED_VARIABLE))
        return var.as_bool() if var else False


