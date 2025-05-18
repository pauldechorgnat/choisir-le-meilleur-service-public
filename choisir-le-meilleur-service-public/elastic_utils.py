import logging
from elasticsearch import Elasticsearch, helpers, BadRequestError


def create_index(
    es: Elasticsearch,
    index_name: str,
) -> None:
    try:
        es.indices.create(
            index=index_name,
        )
    except BadRequestError:
        print("Index already exists")


def insert_offerings(
    es: Elasticsearch,
    index_name: str,
    docs: list[dict],
    chunk_size: int = 500,
    request_timeout: int = 60,
) -> None:
    """
    Insère des documents dans Elasticsearch en utilisant l'API bulk.

    :param es: Instance du client Elasticsearch.
    :param index_name: Nom de l'index cible.
    :param docs: Liste des documents à insérer.
    :param chunk_size: Nombre de documents par lot.
    :param request_timeout: Temps d'attente maximal pour chaque requête.
    """
    actions = (
        {
            "_op_type": "index",
            "_index": index_name,
            # "_id": doc.get("Référence", "Pas de référence") + doc.get("Organisme", "Pas d'organisme"),
            "_source": doc,
        }
        for doc in docs
    )

    try:
        success, errors = helpers.bulk(
            client=es,
            actions=actions,
            # chunk_size=chunk_size,
            # request_timeout=request_timeout,
            # raise_on_error=False,
        )
        if errors:
            logging.error(f"Erreurs lors de l'insertion : {errors}")
        else:
            logging.info(f"{success} documents insérés avec succès.")
    except BadRequestError as e:
        logging.error(f"Erreur d'indexation en masse : {e.errors}")
    except Exception as e:
        logging.error(f"Erreur inattendue : {e}")


def delete_all_offerings(
    es: Elasticsearch,
    index_name: str,
) -> None:
    es.delete_by_query(
        index=index_name,
        body={
            "query": {
                "match_all": {},
            }
        },
    )


def search_offerings(
    es: Elasticsearch,
    index_name: str,
    query: str,
    fields: list[str],
) -> list[dict]:
    body = {
        "query": {
            "multi_match": {
                "query": query,
                "fields": fields,
            }
        }
    }
    res = es.search(index=index_name, body=body)
    return [hit["_source"] for hit in res["hits"]["hits"]]


def get_offering_by_id(
    es: Elasticsearch,
    index_name: str,
    doc_id: str,
) -> dict | None:
    try:
        res = es.get(index=index_name, id=doc_id)
        return res["_source"]
    except Exception:
        return None


def count_offerings(
    es: Elasticsearch,
    index_name: str,
) -> int:
    res = es.count(index=index_name)
    return res["count"]


if __name__ == "__main__":
    from argparse import ArgumentParser
    from utils import read_csv

    argument_parser = ArgumentParser()

    argument_parser.add_argument(
        "--index-name",
        help="Index Name",
        default="offerings",
    )
    argument_parser.add_argument(
        "--elastic-search-host",
        help="ElasticSearch host",
        default="http://0.0.0.0:9200",
    )
    argument_parser.add_argument(
        "-i",
        "--input-file",
        help="Input file",
        default="data/offres-datagouv-20250427.csv",
    )

    arguments = argument_parser.parse_args()

    input_file = arguments.input_file
    offerings = read_csv(input_file)

    elastic_search_host = arguments.elastic_search_host
    elastic_search_client = Elasticsearch(elastic_search_host)

    index_name = arguments.index_name

    create_index(
        es=elastic_search_client,
        index_name=index_name,
    )

    print("Deleting previous offerings from `offerings` index")
    delete_all_offerings(
        es=elastic_search_client,
        index_name=index_name,
    )

    print(f"Trying to insert {len(offerings)} into `offerings` index")
    insert_offerings(
        es=elastic_search_client,
        index_name=index_name,
        docs=offerings,
    )

    n_documents = count_offerings(
        es=elastic_search_client,
        index_name=index_name,
    )

    print(f"{n_documents} in `offerings` index")
