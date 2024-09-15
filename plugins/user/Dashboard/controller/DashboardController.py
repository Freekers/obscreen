from flask import Flask, render_template

from src.interface.ObController import ObController


class DashboardController(ObController):

    def register(self):
        self._app.add_url_rule('/dashboard', 'dashboard', self.dashboard, methods=['GET'])

    def dashboard(self):
        return self.render_view(
            '@dashboard.jinja.html',
            count_playlists=len(self._model_store.playlist().get_all())
        )
