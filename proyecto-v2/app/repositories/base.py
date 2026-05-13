from abc import ABC, abstractmethod
from typing import List, Optional, TypeVar, Generic

T = TypeVar('T')


class BaseRepository(ABC, Generic[T]):
    """Clase base abstracta para todos los repositorios."""

    @abstractmethod
    def create(self, entity: T) -> T:
        """Crear una entidad."""
        pass

    @abstractmethod
    def get_by_id(self, entity_id: str) -> Optional[T]:
        """Obtener entidad por ID."""
        pass

    @abstractmethod
    def get_all(self) -> List[T]:
        """Obtener todas las entidades."""
        pass

    @abstractmethod
    def update(self, entity_id: str, entity: T) -> Optional[T]:
        """Actualizar una entidad."""
        pass

    @abstractmethod
    def delete(self, entity_id: str) -> bool:
        """Eliminar una entidad."""
        pass
