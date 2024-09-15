from enum import Enum
from typing import Union, Dict, Optional

from src.manager.LangManager import LangManager
from src.manager.VariableManager import VariableManager
from src.manager.DatabaseManager import DatabaseManager


class ModelManager:

    def __init__(self, lang_manager: LangManager, database_manager: DatabaseManager, variable_manager: VariableManager):
        self._lang_manager = lang_manager
        self._database_manager = database_manager
        self._variable_manager = variable_manager

    def t(self, token) -> Union[Dict, str]:
        return self.lang_manager.translate(token)

    @property
    def lang_manager(self) -> LangManager:
        return self._lang_manager

    @property
    def database_manager(self) -> DatabaseManager:
        return self._database_manager

    @property
    def variable_manager(self) -> VariableManager:
        return self._variable_manager


