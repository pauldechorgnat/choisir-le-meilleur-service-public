import os
import csv
from datetime import datetime
import requests
from elasticsearch import Elasticsearch
from models import Offering


def read_csv(file_path) -> list[dict]:
    """
    Reads a semicolon-separated CSV file (French format) and returns its content as a list of dictionaries.

    """
    try:
        with open(file_path, mode="r", encoding="utf-8") as file:
            reader = csv.DictReader(file, delimiter=";")
            return list(reader)
    except Exception as e:
        print(f"Erreur lors de la lecture du fichier : {e}")
        return []


def download_file(url, save_dir="./"):
    """
    Downloads a file from a given URL and saves it with today's date in the filename.
    """
    today_str = datetime.now().strftime("%Y-%m-%d")
    file_path = os.path.join(save_dir, f"fichier_{today_str}.csv")

    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise error for bad status codes
        with open(file_path, "wb") as f:
            f.write(response.content)
        print(f"Fichier téléchargé avec succès : {file_path}")
        return file_path
    except Exception as e:
        print(f"Erreur lors du téléchargement du fichier : {e}")
        return None


def read_offerings_from_file(file_path: str) -> list[Offering]:
    offerings = read_csv(file_path=file_path)
    return [Offering(**o) for o in offerings]


def search_documents(
    elastic_search_client: Elasticsearch,
    index_name: str,
    text_query: str,
    fields: list[str],
    page_size: int = 10,
    page_number: int = 0,
) -> tuple[list[dict], int]:
    query = {
        "multi_match": {
            "query": text_query,
            "fields": fields,
        }
    }
    count = elastic_search_client.count(
        index=index_name,
        query=query,
    )
    res = elastic_search_client.search(
        index=index_name,
        query=query,
        size=page_size,
        from_=page_size * page_number,
    )
    return (
        [hit["_source"] for hit in res["hits"]["hits"]],
        count["count"],
    )


def get_document_by_id(
    elastic_search_client: Elasticsearch,
    index_name: str,
    doc_id: str,
) -> dict | None:
    try:
        res = elastic_search_client.get(index=index_name, id=doc_id)
        return res["_source"]
    except Exception:
        return None


def get_offering(
    elastic_search_client: Elasticsearch,
    offering_id: str,
    index_name: str = "offerings",
) -> dict | None:
    offering = get_document_by_id(
        elastic_search_client=elastic_search_client,
        index_name=index_name,
        doc_id=offering_id,
    )
    # return Offering(**offering) if offering is not None else None
    return offering


def search_offerings(
    elastic_search_client: Elasticsearch,
    text_query: str,
    index_name: str = "offerings",
    fields: list[str] = ["job_title"],
    page_number: int = 0,
) -> tuple[list[dict], int]:
    offerings, total = search_documents(
        elastic_search_client=elastic_search_client,
        index_name=index_name,
        text_query=text_query,
        fields=fields,
        page_number=page_number,
        page_size=20,
    )

    # return [Offering(**o) for o in offerings], len(offerings)
    return sorted(
        offerings,
        key=lambda x: x["first_publication_date"],
        reverse=True,
    ), total


def parse_input(query: str):
    return query
