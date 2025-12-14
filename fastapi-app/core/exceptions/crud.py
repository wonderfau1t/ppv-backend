from .basic import AppError


class NotFoundError(AppError):
    pass


class AlreadyExistsError(AppError):
    pass
