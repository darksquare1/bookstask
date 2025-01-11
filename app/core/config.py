from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DB_HOST: str
    DB_PORT: str
    DB_USER: str
    DB_PASS: str
    DB_NAME: str
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    DB_TEST_HOST: str
    DB_TEST_PORT: str
    DB_TEST_USER: str
    DB_TEST_PASS: str
    DB_TEST_NAME: str

    @property
    def DATABASE_URL(self):
        return f'postgresql://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}'

    @property
    def TEST_DATABASE_URL(self):
        return f'postgresql://{self.DB_TEST_USER}:{self.DB_TEST_PASS}@{self.DB_TEST_HOST}:{self.DB_TEST_PORT}/{self.DB_TEST_NAME}'

    model_config = SettingsConfigDict(env_file='.env')


settings = Settings()
