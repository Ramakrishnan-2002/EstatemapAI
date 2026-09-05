from sqlalchemy.ext.asyncio import AsyncSession


class FavoriteRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
