import datetime
import random

from utils import read_csv

COMPANIES = ["DITP", "MAE", "Cour de cassation"]

OFFERINGS = [
    {
        "id": f"id_{i}",
        "name": "Super poste à pourvoir",
        "company": random.choice(COMPANIES),
        "publication_date": datetime.date(year=j, month=i, day=1),
    }
    for i in range(1, 13)
    for j in range(2020, 2025)
]

OFFERINGS = [
    {
        "id": f"id_{i}",
        "name": d["Intitulé du poste"],
        "company": d["Organisme de rattachement"],
        "publication_date": d["Date de début de publication par défaut"],
    }
    for i, d in enumerate(read_csv(file_path="./data/offres-datagouv-20250427.csv"))
][:127]


def get_offering(offering_id: str) -> dict | None:
    for offering in OFFERINGS:
        if offering["id"] == offering_id:
            return offering
    return None


def search_offering(
    page_number: int,
    search_query: str | None = None,
    start_date: datetime.date | None = None,
    end_date: datetime.date | None = None,
    companies: list[str] | None = None,
):
    random_offerings = random.choices(OFFERINGS, k=random.randint(0, len(OFFERINGS)))
    return random_offerings, len(random_offerings)


def parse_input(query_string):
    return {}
