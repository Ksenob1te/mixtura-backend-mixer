import configparser
import os
import enum
from typing import Dict, Set, Any
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import BaseModel, Field, PrivateAttr


class LocalSettings(BaseSettings):
    model_config = SettingsConfigDict(extra="ignore")


class PostgresConfig(LocalSettings):
    host: str = Field(default="localhost", alias="POSTGRES_HOST")
    port: int = Field(default=5432, alias="POSTGRES_PORT")
    user: str = Field(default="postgres", alias="POSTGRES_USER")
    password: str = Field(default="pgAdminPassword", alias="POSTGRES_PASSWORD")
    db: str = Field(default="mixtura-auth", alias="POSTGRES_DB")

    @property
    def url(self) -> str:
        return f"postgresql+asyncpg://{self.user}:{self.password}@{self.host}:{self.port}/{self.db}"


class RedisConfig(LocalSettings):
    host: str = Field(default="localhost", alias="REDIS_HOST")
    port: int = Field(default=6379, alias="REDIS_PORT")
    user: str = Field(default="default", alias="REDIS_USER")
    password: str = Field(default="", alias="REDIS_PASSWORD")

    @property
    def url(self) -> str:
        return f"redis://{self.user}:{self.password}@{self.host}:{self.port}"


class RabbitConfig(LocalSettings):
    host: str = Field(default="localhost", alias="RABBITMQ_HOST")
    port: int = Field(default=5672, alias="RABBITMQ_PORT")
    user: str = Field(default="guest", alias="RABBITMQ_USER")
    password: str = Field(default="guest", alias="RABBITMQ_PASSWORD")
    vhost: str = Field(default="/", alias="RABBITMQ_VHOST")

    @property
    def url(self) -> str:
        return f"amqp://{self.user}:{self.password}@{self.host}:{self.port}{self.vhost}"


class EventFlowConfig(BaseModel):
    transitions: Dict[str, Set[str]]
    _transition_map: Dict[Any, Set[Any]] | None = PrivateAttr(default=None)

    def get_transitions(self, enum_cls: type[enum.Enum]) -> Dict[Any, Set[Any]] | None:
        if self._transition_map is None:
            self._transition_map = {}
            for src_name, targets in self.transitions.items():
                if src_name not in enum_cls.__members__:
                    continue
                source_state = enum_cls[src_name]
                valid_targets = {enum_cls[t] for t in targets if t in enum_cls.__members__}
                self._transition_map[source_state] = valid_targets
        return self._transition_map

    @classmethod
    def load_from_ini(cls) -> "EventFlowConfig":
        config_parser = configparser.ConfigParser()
        current_dir = os.path.dirname(os.path.abspath(__file__))
        config_path = os.path.join(current_dir, 'config', 'event_flow.ini')

        if os.path.exists(config_path):
            config_parser.read(config_path)

        transitions = {}
        if 'Transitions' in config_parser:
            for key, val in config_parser['Transitions'].items():
                targets = {t.strip().upper() for t in val.split(',') if t.strip()}
                transitions[key.upper()] = targets

        return cls(transitions=transitions)


class Env(LocalSettings):
    redis: RedisConfig = Field(default_factory=RedisConfig)
    rabbit: RabbitConfig = Field(default_factory=RabbitConfig)
    postgres: PostgresConfig = Field(default_factory=PostgresConfig)
    event_flow: EventFlowConfig = Field(default_factory=EventFlowConfig.load_from_ini)
    team_formation_variants_ttl_seconds: int = Field(default=3600, alias="TEAM_FORMATION_VARIANTS_TTL_SECONDS")
    rabbit_request_timeout: float = Field(default=30.0, alias="RABBIT_REQUEST_TIMEOUT")

    @classmethod
    def load(cls) -> "Env":
        return cls()


env = Env.load()
