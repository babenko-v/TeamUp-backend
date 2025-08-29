from application.uow.interfaces import IUnitOfWork
from infrastructure.database.repositories.user_repo import UserRepository


class UnitOfWork(IUnitOfWork):
    def __init__(self, session_factory):
        self.session_factory = session_factory

    async def __aenter__(self):
        self.session = self.session_factory()

        self.users = UserRepository(self.session)

        return await super().__aenter__()

    async def commit(self):
        await self.session.commit()

    async def rollback(self):
        await self.session.rollback()