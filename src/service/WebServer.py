import os
import time
from waitress import serve
from functools import wraps

from flask import Flask, send_from_directory, redirect, url_for, request, jsonify, make_response, abort

from src.service.ModelStore import ModelStore
from src.service.TemplateRenderer import TemplateRenderer
from src.controller.PlayerController import PlayerController
from src.controller.SlideController import SlideController
from src.controller.ContentController import ContentController
from src.controller.PlaylistController import PlaylistController
from src.controller.SysinfoController import SysinfoController
from src.controller.SettingsController import SettingsController
from src.controller.CoreController import CoreController
from src.constant.WebDirConstant import WebDirConstant
from src.exceptions.HttpClientException import HttpClientException


class WebServer:

    def __init__(self, kernel, model_store: ModelStore, template_renderer: TemplateRenderer):
        self._app = None
        self._kernel = kernel
        self._model_store = model_store
        self._template_renderer = template_renderer
        self._debug = self._model_store.config().map().get('debug')
        self.setup()

    def get_max_upload_size(self):
        return self._model_store.variable().map().get('slide_upload_limit').as_int() * 1024 * 1024

    def run(self) -> None:
        serve(
            self._app,
            host=self._model_store.config().map().get('bind'),
            port=self._model_store.config().map().get('port'),
            threads=100,
            max_request_body_size=self.get_max_upload_size(),
        )

    def reload(self) -> None:
        self.setup()

    def setup(self) -> None:
        self._setup_flask_app()
        self._setup_web_globals()
        self._setup_web_errors()
        self._setup_web_controllers()

    def get_app(self):
        return self._app

    def get_template_dir(self) -> str:
        return "{}/{}".format(self._kernel.get_application_dir(), WebDirConstant.FOLDER_TEMPLATES)

    def get_static_dir(self) -> str:
        return "{}/{}".format(self._kernel.get_application_dir(), WebDirConstant.FOLDER_STATIC)

    def get_web_dir(self) -> str:
        return "{}/{}/{}".format(self._kernel.get_application_dir(), WebDirConstant.FOLDER_STATIC, WebDirConstant.FOLDER_STATIC_WEB_ASSETS)

    def get_plugin_static_dst_dir(self, plugin_id: str) -> str:
        return "{}/{}/{}".format(self.get_web_dir(), WebDirConstant.FOLDER_PLUGIN_STATIC_DST, plugin_id)

    def _setup_flask_app(self) -> None:
        self._app = Flask(
            __name__,
            template_folder=self.get_template_dir(),
            static_folder=self.get_static_dir(),
        )

        self._app.config['UPLOAD_FOLDER'] = "{}/{}".format(WebDirConstant.FOLDER_STATIC, WebDirConstant.FOLDER_STATIC_WEB_UPLOADS)
        self._app.config['MAX_CONTENT_LENGTH'] = self.get_max_upload_size()
        self._app.config['ERROR_404_HELP'] = False

        if self._debug:
            self._app.config['TEMPLATES_AUTO_RELOAD'] = True

    def _setup_web_controllers(self) -> None:
        CoreController(self._kernel, self, self._app, self._model_store, self._template_renderer)
        PlayerController(self._kernel, self, self._app, self._model_store, self._template_renderer)
        SlideController(self._kernel, self, self._app, self._model_store, self._template_renderer)
        ContentController(self._kernel, self, self._app, self._model_store, self._template_renderer)
        SettingsController(self._kernel, self, self._app, self._model_store, self._template_renderer)
        SysinfoController(self._kernel, self, self._app, self._model_store, self._template_renderer)
        PlaylistController(self._kernel, self, self._app, self._model_store, self._template_renderer)

    def _setup_web_globals(self) -> None:
        @self._app.context_processor
        def inject_global_vars() -> dict:
            return self._template_renderer.get_view_globals()

    def _setup_web_errors(self) -> None:
        def handle_error(error):
            if request.headers.get('Content-Type') == 'application/json' or request.headers.get('Accept') == 'application/json':
                response = jsonify({
                    'error': {
                        'code': error.code,
                        'message': error.description
                    }
                })
                return make_response(response, error.code)

            if error.code == 404:
                return send_from_directory(self.get_template_dir(), 'core/error404.html'), 404

            return error

        self._app.register_error_handler(400, handle_error)
        self._app.register_error_handler(404, handle_error)
        self._app.register_error_handler(409, handle_error)
        self._app.register_error_handler(HttpClientException, handle_error)

