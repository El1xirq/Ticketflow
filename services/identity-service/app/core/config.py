from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, FilePath

from functools import cached_property

class Settings(BaseSettings):
    db_url: str = Field(validation_alias="DATABASE_URL")
    db_sync_url: str = Field(validation_alias="SYNC_DATABASE_URL")
    test_db: str = Field(validation_alias="TEST_DATABASE_URL")
    postgres_user: str
    postgres_password: str
    postgres_db: str

    private_key_path: FilePath = Field(validation_alias="JWT_PRIVATE_KEY_PATH")
    public_key_path: FilePath = Field(validation_alias="JWT_PUBLIC_KEY_PATH")
    algorithm: str
    access_token_expire: int = Field(validation_alias="ACCESS_TOKEN_EXPIRE_MINUTES")
    refresh_token_expire: int = Field(validation_alias="REFRESH_TOKEN_EXPIRE_DAYS")
    debug: bool

    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8')

    @cached_property
    def private_key(self) -> str:
        return self.private_key_path.read_text(encoding="utf-8")

    @cached_property
    def public_key(self) -> str:
        return self.public_key_path.read_text(encoding="utf-8")

settings = Settings()