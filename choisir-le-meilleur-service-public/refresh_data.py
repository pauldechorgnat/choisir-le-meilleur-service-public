import logging
from elasticsearch import Elasticsearch, helpers, BadRequestError
from models import format_data
from utils import read_csv
import time


logger = logging.getLogger("search-engine-logger")
logger.setLevel(logging.INFO)

handler = logging.StreamHandler()
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)

logger.addHandler(handler)


def wait_for_elasticsearch(
    elastic_search_client: Elasticsearch,
    retries: int = 30,
):
    for i in range(retries):
        try:
            health = elastic_search_client.cluster.health(
                wait_for_status="green",
            )
            status = health["status"]
            if status == "green":
                logger.info("✅ Elasticsearch is ready!")
                return
            else:
                logger.info("❌ Elasticsearch is not ready.")
        except Exception:
            logger.info("❌ Could not connect to Elasticsearch")

        time.sleep(5)


def count_documents(
    elastic_search_client: Elasticsearch,
    index_name: str,
) -> int:
    res = elastic_search_client.count(index=index_name)
    return res["count"]


def refresh_data(
    file_path: str,
    index_name: str,
    elastic_search_client: Elasticsearch,
    id_field: str = "id",
):
    wait_for_elasticsearch(
        elastic_search_client=elastic_search_client,
    )
    logger.info("Trying to create index")

    try:
        elastic_search_client.indices.create(
            index=index_name,
        )
    except BadRequestError:
        logger.info("Index already exists")

    n_documents = count_documents(
        elastic_search_client=elastic_search_client,
        index_name=index_name,
    )

    logger.info(f"Reading documents to insert from '{file_path}'")
    documents = [format_data(d) for d in read_csv(file_path=file_path)]
    logger.info(f"Found {len(documents)} documents to insert in {index_name} index")

    logger.info(f"Found {n_documents} already in {index_name} index")
    logger.info("Deleting documents ...")
    delete_all_documents(
        elastic_search_client=elastic_search_client,
        index_name=index_name,
    )
    logger.info("Documents deleted")
    logger.info("Inserting documents")
    insert_documents(
        elastic_search_client=elastic_search_client,
        index_name=index_name,
        docs=documents,
        id_field=id_field,
    )
    n_documents = count_documents(
        elastic_search_client=elastic_search_client,
        index_name=index_name,
    )
    logger.info(f"Found {n_documents} in {index_name} index")


def create_index(
    elastic_search_client: Elasticsearch,
    index_name: str,
) -> None:
    try:
        elastic_search_client.indices.create(
            index=index_name,
        )
    except BadRequestError:
        logger.info("Index already exists")


def insert_documents(
    elastic_search_client: Elasticsearch,
    index_name: str,
    docs: list[dict],
    id_field: str = "id",
) -> None:
    actions = (
        {
            "_op_type": "index",
            "_index": index_name,
            "_source": doc,
            "_id": doc.get(id_field),
        }
        for doc in docs
    )

    success, errors = helpers.bulk(
        client=elastic_search_client,
        actions=actions,
    )


def delete_all_documents(
    elastic_search_client: Elasticsearch,
    index_name: str,
) -> None:
    elastic_search_client.delete_by_query(
        index=index_name,
        body={
            "query": {
                "match_all": {},
            }
        },
    )


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

    elastic_search_host = arguments.elastic_search_host
    elastic_search_client = Elasticsearch(elastic_search_host)

    index_name = arguments.index_name

    refresh_data(
        file_path=input_file,
        index_name=index_name,
        elastic_search_client=elastic_search_client,
        id_field="reference",
    )
