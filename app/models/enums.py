from enum import StrEnum


class Gender(StrEnum):
    MASCULINE = "masculine"
    FEMININE = "feminine"
    UNISEX = "unisex"


class Concentration(StrEnum):
    EDC = "edc"  # Eau de Cologne
    EDT = "edt"  # Eau de Toilette
    EDP = "edp"  # Eau de Parfum
    PARFUM = "parfum"
    EXTRAIT = "extrait"


class NoteLayer(StrEnum):
    TOP = "top"  # notas de topo (saída)
    HEART = "heart"  # notas de coração (corpo)
    BASE = "base"  # notas de fundo


class UserRole(StrEnum):
    USER = "user"
    ADMIN = "admin"
