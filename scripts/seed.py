"""Popula o banco com marcas, notas olfativas e perfumes de exemplo.

O script é idempotente: pode ser rodado várias vezes sem duplicar nada.
Marcas, notas e perfumes que já existem são mantidos como estão.

Uso:
    python -m scripts.seed
    python -m scripts.seed --with-reviews

Com --with-reviews, também cria alguns usuários de demonstração (que não
conseguem fazer login, porque recebem uma senha aleatória descartada) e
reviews deles, para a média e o ranking terem dados.

As pirâmides olfativas são simplificadas e servem como dados de exemplo.
"""

import argparse
import random
import secrets

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.security import hash_password
from app.db.session import SessionLocal
from app.models import (
    Brand,
    Concentration,
    Gender,
    Note,
    NoteLayer,
    Perfume,
    PerfumeNote,
    Review,
    User,
)

BRANDS = {
    "Dior": "França",
    "Chanel": "França",
    "Creed": "França",
    "Paco Rabanne": "França",
    "Yves Saint Laurent": "França",
    "Lancôme": "França",
    "Jean Paul Gaultier": "França",
    "Maison Francis Kurkdjian": "França",
    "Giorgio Armani": "Itália",
    "Versace": "Itália",
    "Carolina Herrera": "Estados Unidos",
    "Tom Ford": "Estados Unidos",
}

PERFUMES = [
    {
        "name": "Sauvage",
        "brand": "Dior",
        "year": 2015,
        "gender": Gender.MASCULINE,
        "concentration": Concentration.EDT,
        "perfumer": "François Demachy",
        "top": ["Bergamota", "Pimenta"],
        "heart": ["Lavanda", "Pimenta de Sichuan", "Gerânio"],
        "base": ["Ambroxan", "Cedro", "Ládano"],
    },
    {
        "name": "J'adore",
        "brand": "Dior",
        "year": 1999,
        "gender": Gender.FEMININE,
        "concentration": Concentration.EDP,
        "perfumer": "Calice Becker",
        "top": ["Pera", "Melão", "Pêssego", "Bergamota"],
        "heart": ["Jasmim", "Lírio-do-vale", "Tuberosa", "Rosa"],
        "base": ["Almíscar", "Baunilha", "Cedro"],
    },
    {
        "name": "Bleu de Chanel",
        "brand": "Chanel",
        "year": 2010,
        "gender": Gender.MASCULINE,
        "concentration": Concentration.EDT,
        "perfumer": "Jacques Polge",
        "top": ["Toranja", "Limão", "Hortelã", "Pimenta Rosa"],
        "heart": ["Gengibre", "Noz-moscada", "Jasmim"],
        "base": ["Incenso", "Vetiver", "Cedro", "Sândalo"],
    },
    {
        "name": "Coco Mademoiselle",
        "brand": "Chanel",
        "year": 2001,
        "gender": Gender.FEMININE,
        "concentration": Concentration.EDP,
        "perfumer": "Jacques Polge",
        "top": ["Laranja", "Bergamota"],
        "heart": ["Rosa", "Jasmim", "Lichia"],
        "base": ["Patchouli", "Vetiver", "Baunilha", "Almíscar"],
    },
    {
        "name": "Nº 5",
        "brand": "Chanel",
        "year": 1921,
        "gender": Gender.FEMININE,
        "concentration": Concentration.EDP,
        "perfumer": "Ernest Beaux",
        "top": ["Aldeídos", "Ylang-ylang", "Néroli", "Bergamota"],
        "heart": ["Íris", "Jasmim", "Rosa", "Lírio-do-vale"],
        "base": ["Sândalo", "Vetiver", "Baunilha", "Almíscar"],
    },
    {
        "name": "Aventus",
        "brand": "Creed",
        "year": 2010,
        "gender": Gender.MASCULINE,
        "concentration": Concentration.EDP,
        "perfumer": "Olivier Creed",
        "top": ["Abacaxi", "Bergamota", "Groselha Negra", "Maçã"],
        "heart": ["Bétula", "Patchouli", "Jasmim", "Rosa"],
        "base": ["Almíscar", "Musgo de Carvalho", "Âmbar-gris", "Baunilha"],
    },
    {
        "name": "1 Million",
        "brand": "Paco Rabanne",
        "year": 2008,
        "gender": Gender.MASCULINE,
        "concentration": Concentration.EDT,
        "perfumer": "Christophe Raynaud, Olivier Pescheux, Michel Girard",
        "top": ["Toranja", "Hortelã", "Mandarina"],
        "heart": ["Rosa", "Canela"],
        "base": ["Couro", "Âmbar", "Patchouli"],
    },
    {
        "name": "Black Opium",
        "brand": "Yves Saint Laurent",
        "year": 2014,
        "gender": Gender.FEMININE,
        "concentration": Concentration.EDP,
        "perfumer": "Nathalie Lorson, Marie Salamagne, Olivier Cresp, Honorine Blanc",
        "top": ["Pera", "Pimenta Rosa", "Flor de Laranjeira"],
        "heart": ["Café", "Jasmim", "Amêndoa", "Alcaçuz"],
        "base": ["Baunilha", "Patchouli", "Cedro"],
    },
    {
        "name": "Y",
        "brand": "Yves Saint Laurent",
        "year": 2018,
        "gender": Gender.MASCULINE,
        "concentration": Concentration.EDP,
        "perfumer": "Dominique Ropion",
        "top": ["Maçã", "Gengibre", "Bergamota"],
        "heart": ["Sálvia", "Gerânio", "Zimbro"],
        "base": ["Âmbar", "Fava Tonka", "Cedro", "Vetiver"],
    },
    {
        "name": "La Vie Est Belle",
        "brand": "Lancôme",
        "year": 2012,
        "gender": Gender.FEMININE,
        "concentration": Concentration.EDP,
        "perfumer": "Olivier Polge, Dominique Ropion, Anne Flipo",
        "top": ["Groselha Negra", "Pera"],
        "heart": ["Íris", "Jasmim", "Flor de Laranjeira"],
        "base": ["Pralinê", "Baunilha", "Patchouli", "Fava Tonka"],
    },
    {
        "name": "Le Male",
        "brand": "Jean Paul Gaultier",
        "year": 1995,
        "gender": Gender.MASCULINE,
        "concentration": Concentration.EDT,
        "perfumer": "Francis Kurkdjian",
        "top": ["Lavanda", "Hortelã", "Cardamomo", "Bergamota"],
        "heart": ["Canela", "Flor de Laranjeira", "Cominho"],
        "base": ["Baunilha", "Fava Tonka", "Âmbar", "Sândalo"],
    },
    {
        "name": "Baccarat Rouge 540",
        "brand": "Maison Francis Kurkdjian",
        "year": 2015,
        "gender": Gender.UNISEX,
        "concentration": Concentration.EDP,
        "perfumer": "Francis Kurkdjian",
        "top": ["Açafrão", "Jasmim"],
        "heart": ["Amberwood", "Âmbar-gris"],
        "base": ["Resina de Abeto", "Cedro"],
    },
    {
        "name": "Acqua di Giò",
        "brand": "Giorgio Armani",
        "year": 1996,
        "gender": Gender.MASCULINE,
        "concentration": Concentration.EDT,
        "perfumer": "Alberto Morillas",
        "top": ["Limão", "Bergamota", "Néroli", "Mandarina"],
        "heart": ["Notas Marinhas", "Jasmim", "Alecrim", "Pêssego"],
        "base": ["Almíscar", "Cedro", "Musgo de Carvalho", "Patchouli"],
    },
    {
        "name": "Eros",
        "brand": "Versace",
        "year": 2012,
        "gender": Gender.MASCULINE,
        "concentration": Concentration.EDT,
        "perfumer": "Aurélien Guichard",
        "top": ["Hortelã", "Maçã", "Limão"],
        "heart": ["Fava Tonka", "Ambroxan", "Gerânio"],
        "base": ["Baunilha", "Vetiver", "Musgo de Carvalho", "Cedro"],
    },
    {
        "name": "Good Girl",
        "brand": "Carolina Herrera",
        "year": 2016,
        "gender": Gender.FEMININE,
        "concentration": Concentration.EDP,
        "perfumer": "Louise Turner",
        "top": ["Amêndoa", "Café"],
        "heart": ["Tuberosa", "Jasmim", "Flor de Laranjeira"],
        "base": ["Fava Tonka", "Cacau", "Baunilha"],
    },
    {
        "name": "Oud Wood",
        "brand": "Tom Ford",
        "year": 2007,
        "gender": Gender.UNISEX,
        "concentration": Concentration.EDP,
        "perfumer": "Richard Herpin",
        "top": ["Pau-rosa", "Cardamomo", "Pimenta"],
        "heart": ["Oud", "Sândalo", "Vetiver"],
        "base": ["Fava Tonka", "Baunilha", "Âmbar"],
    },
]

DEMO_REVIEWERS = ["Ana", "Bruno", "Carla", "Diego", "Elisa"]

DEMO_COMMENTS = [
    "Fixação excelente, dura o dia inteiro.",
    "Muito versátil, uso tanto no trabalho quanto à noite.",
    "Projeção forte nas primeiras horas, depois fica mais próximo da pele.",
    "Recebi vários elogios usando.",
    "Bonito, mas achei doce demais para o calor.",
    "Um clássico. Entendo por que é tão famoso.",
    "A saída é incrível, mas o fundo não me agradou tanto.",
    None,
]

LAYERS = [("top", NoteLayer.TOP), ("heart", NoteLayer.HEART), ("base", NoteLayer.BASE)]


def get_or_create_brand(db: Session, name: str, country: str) -> Brand:
    brand = db.scalar(select(Brand).where(func.lower(Brand.name) == name.lower()))
    if brand is None:
        brand = Brand(name=name, country=country)
        db.add(brand)
    return brand


def get_or_create_note(db: Session, name: str, cache: dict[str, Note]) -> Note:
    key = name.lower()
    if key not in cache:
        note = db.scalar(select(Note).where(func.lower(Note.name) == key))
        if note is None:
            note = Note(name=name)
            db.add(note)
        cache[key] = note
    return cache[key]


def perfume_exists(db: Session, brand: Brand, name: str) -> bool:
    if brand.id is None:
        return False
    stmt = select(Perfume.id).where(
        Perfume.brand_id == brand.id,
        func.lower(Perfume.name) == name.lower(),
    )
    return db.scalar(stmt) is not None


def seed_catalog(db: Session) -> int:
    brands = {
        name: get_or_create_brand(db, name, country) for name, country in BRANDS.items()
    }
    db.flush()

    note_cache: dict[str, Note] = {}
    created = 0

    for data in PERFUMES:
        brand = brands[data["brand"]]
        if perfume_exists(db, brand, data["name"]):
            continue

        perfume_notes = [
            PerfumeNote(note=get_or_create_note(db, note_name, note_cache), layer=layer)
            for key, layer in LAYERS
            for note_name in data[key]
        ]
        db.add(
            Perfume(
                name=data["name"],
                brand=brand,
                release_year=data["year"],
                gender=data["gender"],
                concentration=data["concentration"],
                perfumer=data["perfumer"],
                notes=perfume_notes,
            )
        )
        created += 1

    db.commit()
    return created


def seed_reviews(db: Session) -> int:
    rng = random.Random(42)
    perfumes = list(db.scalars(select(Perfume)))
    created = 0

    for index, name in enumerate(DEMO_REVIEWERS, start=1):
        email = f"demo.{name.lower()}@example.com"
        user = db.scalar(select(User).where(User.email == email))
        if user is None:
            user = User(
                email=email,
                name=name,
                hashed_password=hash_password(secrets.token_urlsafe(32)),
            )
            db.add(user)
            db.flush()

        for perfume in rng.sample(perfumes, k=min(len(perfumes), 6 + index)):
            already_reviewed = db.scalar(
                select(Review.id).where(
                    Review.author_id == user.id,
                    Review.perfume_id == perfume.id,
                )
            )
            if already_reviewed:
                continue

            db.add(
                Review(
                    author_id=user.id,
                    perfume_id=perfume.id,
                    rating=rng.choice([6, 7, 7, 8, 8, 8, 9, 9, 10]),
                    longevity=rng.randint(2, 5),
                    sillage=rng.randint(2, 5),
                    text=rng.choice(DEMO_COMMENTS),
                )
            )
            created += 1

    db.commit()
    return created


def main() -> None:
    parser = argparse.ArgumentParser(description="Popula o banco com dados de exemplo.")
    parser.add_argument(
        "--with-reviews",
        action="store_true",
        help="cria usuários de demonstração e reviews",
    )
    args = parser.parse_args()

    with SessionLocal() as db:
        perfumes_created = seed_catalog(db)
        print(f"Perfumes criados: {perfumes_created}")

        if args.with_reviews:
            reviews_created = seed_reviews(db)
            print(f"Reviews criadas: {reviews_created}")


if __name__ == "__main__":
    main()
