from enum import Enum


class TransactionStatus(str, Enum):
    PENDING = "PENDING"
    COLLECTED = "COLLECTED"
    DELIVERED = "DELIVERED"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"
