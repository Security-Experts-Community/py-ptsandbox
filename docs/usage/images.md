Getting a list of installed images in the sandbox:

```python
from ptsandbox import Sandbox, SandboxKey, SandboxDownloadArtifactRequst

async def example() -> None:
    sandbox = Sandbox(key=SandboxKey(...))

    images = await sandbox.api.get_images()
    print(images)
```

Response model:

```python
class SandboxImageInfo(SandboxBaseModel):
    """
    Информация об образе виртуальной машины
    Может быть пустым словарем ({}), если песок отрыгнул пустоту.
    (хорошая моделька, ультимативно-опциональная!)
    """

    class OS(SandboxBaseModel):
        """Информация об операционной системе образа виртуальной машины"""

        name: str
        """Название операционной системы"""

        version: str
        """Версия операционной системы"""

        architecture: str
        """Архитектура процессора, которую поддерживает операционная система"""

        service_pack: str | None = None
        """Название пакета обновления операционной системы (есть в ответе от api)"""

        servicePack: str | None = None
        """Название пакета обновления операционной системы (есть в ответе от UI)"""

        locale: str
        """Локаль операционной системы"""

    image_id: str | None = None
    """
    Идентификатор образа виртуальной машины
    Опционален для возможности переиспользования в моделях фронта
    Почему фронт его не возвращает - мистика
    """

    name: str | None = None
    """Новый фронт стал-таки возвращать название образа. Правда, в виде name."""

    type: str | None = None
    """Новое поле на фронте"""

    version: str | None = None
    """
    Версия образа виртуальной машины
    """

    os: OS | None = None
    """
    Информация об операционной системе образа виртуальной машины
    """
```
