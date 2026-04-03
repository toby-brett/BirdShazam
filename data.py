import os
import time
import requests

def get_url(asset_id):
    # api sig
    return f"https://cdn.download.ams.birds.cornell.edu/api/v2/asset/{asset_id}/mp3"

def download_mp3(folder, path, asset_id):
    url = get_url(asset_id)
    r = requests.get(url)
    if r.status_code == 200:
        os.makedirs(folder, exist_ok=True)
        with open(path, "wb") as f:
            f.write(r.content)
    else:
        print(f"Failed: {url}")

def fetch_asset_ids(taxon_code, page_size=100, max_to_fetch=10_000, first_cursor_mark=""):
    api = "https://search.macaulaylibrary.org/api/v1/search"
    asset_ids = []
    cursor_mark = first_cursor_mark

    while True:
        params = {
            "taxonCode": taxon_code,
            "mediaType": "audio",
            "sort": "rating_rank_desc",
            "count": page_size,
            "initialCursorMark": cursor_mark
        }

        resp = requests.get(api, params=params)
        resp.raise_for_status()
        data = resp.json()

        results = data.get("results", {}).get("content", [])
        if not results:
            break

        for item in results:
            asset_ids.append(str(item["assetId"]))

        if len(asset_ids) >= max_to_fetch:
            break

        cursor_mark = data.get("results").get("nextCursorMark")
        print(f"Cursor mark: {cursor_mark}")
        time.sleep(0.5)

    return set(asset_ids), cursor_mark


def get_data(taxon_code):
    seen_asset_ids = []
    cursor_mark = ""

    for i in range(2):
        asset_ids, cursor_mark = fetch_asset_ids(taxon_code, max_to_fetch=1_000, first_cursor_mark=cursor_mark)

        for num in asset_ids:
            if num in seen_asset_ids:
                print(f"Discarding duplicat {num}")
                continue
            seen_asset_ids.append(num)
            download_mp3(taxon_code, f"{taxon_code}/{num}.mp3", num)

if __name__ == "__main__":
    get_data("greti1")