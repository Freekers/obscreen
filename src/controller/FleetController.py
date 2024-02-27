import json

from flask import Flask, render_template, redirect, request, url_for, jsonify
from src.model.Screen import Screen


class FleetController:

    def __init__(self, app, l, screen_manager):
        self._app = app
        self._l = l
        self._screen_manager = screen_manager
        self.register()

    def register(self):
        self._app.add_url_rule('/fleet', 'fleet', self.fleet, methods=['GET'])
        self._app.add_url_rule('/fleet/screen/add', 'fleet_screen_add', self.fleet_screen_add, methods=['POST'])
        self._app.add_url_rule('/fleet/screen/edit', 'fleet_screen_edit', self.fleet_screen_edit, methods=['POST'])
        self._app.add_url_rule('/fleet/screen/toggle', 'fleet_screen_toggle', self.fleet_screen_toggle, methods=['POST'])
        self._app.add_url_rule('/fleet/screen/delete', 'fleet_screen_delete', self.fleet_screen_delete, methods=['DELETE'])
        self._app.add_url_rule('/fleet/screen/position', 'fleet_screen_position', self.fleet_screen_position, methods=['POST'])

    def fleet(self):
        return render_template(
            'fleet/fleet.jinja.html',
            l=self._l,
            enabled_screens=self._screen_manager.get_enabled_screens(),
            disabled_screens=self._screen_manager.get_disabled_screens(),
        )

    def fleet_screen_add(self):
        self._screen_manager.add_form(Screen(
            name=request.form['name'],
            address=request.form['address'],
        ))
        return redirect(url_for('fleet'))

    def fleet_screen_edit(self):
        self._screen_manager.update_form(request.form['id'], request.form['name'], request.form['address'])
        return redirect(url_for('fleet'))

    def fleet_screen_toggle(self):
        data = request.get_json()
        self._screen_manager.update_enabled(data.get('id'), data.get('enabled'))
        return jsonify({'status': 'ok'})

    def fleet_screen_delete(self):
        data = request.get_json()
        self._screen_manager.delete(data.get('id'))
        return jsonify({'status': 'ok'})

    def fleet_screen_position(self):
        data = request.get_json()
        self._screen_manager.update_positions(data)
        return jsonify({'status': 'ok'})