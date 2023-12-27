from enum import Enum


class UserStatus(Enum):
    ANONYMOUS = "ANONYMOUS"
    USER = "USER"
    ADMIN = "ADMIN"
    SUPER = "SUPER"