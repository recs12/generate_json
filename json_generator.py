import os
import json
import glob
import re
from pampy import match, _
from model import content, template_article, HOSTING_URL_BASE, SECURITY_KEY


def get_link(sku):
    return HOSTING_URL_BASE + sku + SECURITY_KEY


def get_article(sku: str, revision: str, dict) -> dict:
    dict_copy = dict.copy()
    dict_copy["urlName"] = sku
    dict_copy["body"]["title"] = sku
    dict_copy["body"]["altText"] = revision
    dict_copy["body"]["source"]["url"] = get_link(sku)
    return dict_copy


def extract_sku_revision(fileName):
    return match(
        fileName,
        re.compile("(\w+)-Rev-(\d{1,2})"),
        lambda sku, rev: (sku, rev),
        _,
        "something else",
    )


def all_images():
    # rewrite into generator
    imagesJpg = (imageJpg for imageJpg in glob.glob("*.jpg"))
    for jpg in imagesJpg:
        yield extract_sku_revision(jpg)


def create_json(data, file_json):
    with open(file_json, "w") as f:
        json.dump(data, f, indent=4)


def generate_data(image: tuple):
    sku, revision = image
    return get_article(sku, revision, template_article)


# recursion.
def rec_append(serie, content):
    if len(serie) == 0:
        return []
    else:
        sku, revision = serie[0]
        art = get_article(sku, revision, template_article)
        art_copy = art.copy()
        art_copy["body"] = {
            "title": sku,
            "altText": revision,
            "source": {"url": HOSTING_URL_BASE + sku + SECURITY_KEY},
        }
        content["content"].append(art_copy)
        return rec_append(serie[1:], content)


def sliced_by_n(images, n=2000):
    """Slice the images by sequences of n elements."""
    return [images[i : i + n] for i in range(0, len(images), n)]


if __name__ == "__main__":
    for n, sequence in enumerate(sliced_by_n([image for image in all_images()], 4)):
        print(sequence)
        rec_append(sequence, content)
        create_json(content, f"contents{n}.json")
        content = {"content": []}
