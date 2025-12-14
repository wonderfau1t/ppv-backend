from typing import Dict

from core.schemas.table_schemas import ColumnSchema, TableSchema


class SchemaService:
    def __init__(self):
        self._schemas: Dict[str, TableSchema] = {}
        self.register_schemas()

    def register(self, name: str, schema: TableSchema) -> None:
        if name in self._schemas:
            raise ValueError(f"Schema {name} already exists")
        self._schemas[name] = schema

    def get(self, name: str) -> TableSchema:
        schema = self._schemas.get(name)
        if not schema:
            raise ValueError(f"Schema {name} is not exists")

        return schema

    def register_schemas(self):
        # Таблица пользователей
        users = TableSchema(
            columns=[
                ColumnSchema(key="player", title="ФИО Игрока", type="player"),
                ColumnSchema(key="gamesCount", title="Количество сыгранных игр", type="number"),
                ColumnSchema(key="winsCount", title="Количество побед", type="number"),
            ]
        )

        # Таблица пользователей для админа
        admin_users = TableSchema(
            columns=[
                ColumnSchema(key="player", title="ФИО Игрока", type="player"),
                ColumnSchema(key="gamesCount", title="Количество сыгранных игр", type="number"),
                ColumnSchema(key="winsCount", title="Количество побед", type="number"),
                ColumnSchema(key="role", title="Роль", type="role"),
                ColumnSchema(key="status", title="Статус", type="status"),
            ]
        )

        # Общая история матчей
        matches_history = TableSchema(
            columns=[
                ColumnSchema(key="id", title="ID матча", type="str"),
                ColumnSchema(key="date", title="Дата", type="date"),
                ColumnSchema(key="player1", title="Игрок 1", type="player"),
                ColumnSchema(key="player2", title="Игрок 2", type="player"),
                ColumnSchema(key="score", title="Счет", type="str"),
                ColumnSchema(key="winner", title="Победитель", type="player"),
                ColumnSchema(key="type", title="Тип игры", type="str"),
            ]
        )

        # История матчей пользователя
        user_matches_history = TableSchema(
            columns=[
                ColumnSchema(key="id", title="ID матча", type="str"),
                ColumnSchema(key="date", title="Дата", type="date"),
                ColumnSchema(key="opponent", title="Противник", type="player"),
                ColumnSchema(key="score", title="Счет", type="str"),
                ColumnSchema(key="winner", title="Победитель", type="player"),
                ColumnSchema(key="type", title="Тип игры", type="str"),
            ]
        )

        # Счет по партиям
        match_with_sets = TableSchema(
            columns=[
                ColumnSchema(key="player", title="Игрок", type="player"),
                ColumnSchema(key="s1", title="П1", type="number"),
                ColumnSchema(key="s2", title="П2", type="number"),
                ColumnSchema(key="s3", title="П3", type="number"),
                ColumnSchema(key="s4", title="П4", type="number"),
                ColumnSchema(key="s5", title="П5", type="number"),
                ColumnSchema(key="score", title="Счет", type="str"),
            ]
        )

        self.register("users", users)
        self.register("admin-users", admin_users)
        self.register("matches-history", matches_history)
        self.register("user-matches-history", user_matches_history)
        self.register("match-with-sets", match_with_sets)
