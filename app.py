from flask import Flask, render_template, request

from mock import get_offering, search_offering, parse_input

app = Flask(__name__)


@app.get("/")
def render_search():
    if "page-number" in request.args:
        page_number = request.args["page-number"]
    else:
        page_number = 0
    if "search-query" in request.args:
        query_string = request.args["search-query"]
        parameters = parse_input(query_string)
        offerings, total = search_offering(
            page_number=page_number,
        )

        n_pages = total // 25
        if total % 25 > 0:
            n_pages += 1

    else:
        offerings = []
        parameters = {}
        total = None
        query_string = None
        n_pages = None

    min_page = max(int(page_number) - 3, 0)
    max_page = min(n_pages, int(page_number) + 4) if n_pages else 0

    if isinstance(parameters.get("jurisdiction"), list):
        parameters["jurisdiction"] = ", ".join(parameters["jurisdiction"])

    return render_template(
        "index.html",
        documents=offerings,
        parameters=parameters,
        total=total,
        query_string=query_string,
        n_pages=n_pages,
        page_number=int(page_number),
        min_page=min_page,
        max_page=max_page,
    )


@app.get("/offering/<offering_id>")
def get_offering_page(offering_id: str):
    offering = get_offering(offering_id=offering_id)
    if offering is None:
        raise ValueError("Erreur 404") # TODO: faire mieux
    return render_template(
        "offering.html",
        offering=offering,
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=2022, debug=True)
