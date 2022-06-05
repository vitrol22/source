import requests
import json


def query_api(search_url, query, scrollId=None):
    headers = {"Authorization": "solar " + apikey}
    if not scrollId:
        response = requests.get(
            f"{search_url}?q={query}&limit=100&scroll=true", headers=headers
        )
    else:
        response = requests.get(
            f"{search_url}?q={query}&limit=100&scrollId={scrollId}", headers=headers
        )
    return response.json(), response.elapsed.total_seconds()


def scroll(search_url, query, extract_info_callback):
    allresults = []
    count = 0
    scrollId = None
    while True:
        result, elapsed = query_api(search_url, query, scrollId)
        scrollId = result["scrollId"]
        totalhits = result["totalHits"]
        result_size = len(result["results"])
        if result_size == 0:
            break
        for hit in result["results"]:
            if extract_info_callback:
                allresults.append(extract_info_callback(hit))
            else:
                allresults.append(extract_info(hit))
        count += result_size
        print(f"{count}/{totalhits} {elapsed}s")
    return allresults


def extract_info(hit):
    return {"id": hit["id"], "name": hit["name"], "url": hit["oaiPmhUrl"]}


def get_ids(hit):
    return {
        "id": hit["id"],
        "arxivId": hit["arxivId"],
        "doi": hit["doi"],
        "oaiIds": ",".join(hit["oaiIds"]),
        "magId": hit["magId"],
        "coreIds": ",".join(hit["outputs"]),
        "pubmedId": hit["pubmedId"],
    }


apikey = "YhB7wnNIaLJgkbMPV19pc6X5yt3jWliu"
headers = {"Authorization": "Bearer " + apikey}
# response = scroll(
#    "https://api.core.ac.uk/v3/search/works",
#    "dataProviders:https://api.core.ac.uk/v3/data-providers/14",
#    get_ids,
# )

singlework = requests.get(
    f"https://api.core.ac.uk/v3/search/works?q=dataProviders:https://api.core.ac.uk/v3/data-providers/131&limit=1",
    headers=headers,
)
singlework.json()
st_python = json.load(singlework.json)

print(st_python)
