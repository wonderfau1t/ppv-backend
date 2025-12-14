from .basic import AppError


class UnauthorizedError(AppError):
    pass


class InvalidCredentialsError(AppError):
    pass


class ForbiddenError(AppError):
    pass
