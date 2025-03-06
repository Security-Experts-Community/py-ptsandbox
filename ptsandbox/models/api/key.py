from pydantic import BaseModel, Field


class SandboxKey(BaseModel):
    """Класс, описывающий ключ, который должен передаваться в Sandbox"""

    name: str
    """Имя ключа"""

    key: str
    """API ключ для подключения"""

    host: str
    """Хост в формате 1.1.1.1"""

    description: str = ""
    """Описание ключа для удобной работы"""

    max_workers: int = Field(default=1, ge=1)
    """
    Максимальное количество одновременно работающих виртуалок
    Полезно, если стенд не слишком производительный и необходимо изменить параметры
    """

    @property
    def url(self) -> str:
        """https адрес для подключения по API"""

        return f"https://{self.host}/api/v1"

    @property
    def debug_url(self) -> str:
        """https адрес для подключения к debug API"""

        return f"https://{self.host}/api/debug"

    def __repr__(self) -> str:
        return f"{self.name} for {self.host} ({self.max_workers})" + (
            f"({self.description})" if self.description else ""
        )

    def __key(self) -> tuple[str, str, str]:
        return (self.name, self.key, self.host)

    def __hash__(self) -> int:
        return hash(self.__key())

    def __eq__(self, value: object) -> bool:
        if isinstance(value, SandboxKey):
            return self.__key() == value.__key()
        return False
