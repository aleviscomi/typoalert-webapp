import ssdeep, imagehash, os
from html2image import Html2Image
from PIL import Image

hti = Html2Image()

# top 10 alert
def evaluate_t10a(input_domain, ctarget, search_results):
    if input_domain not in search_results and ctarget in search_results:
        return 1
    elif input_domain in search_results and ctarget not in search_results:
        return -1
    return 0


# did you mean alert
def evaluate_dyma(ctarget, dym):
    return 1 if ctarget == dym else 0


# phishing alert (fuzzy-hashing + perceptual-hashing)
def evaluate_pha(visited_domain_html, ctarget_html):
    return 1 if evaluate_fuzzy_hashing(visited_domain_html, ctarget_html) and evaluate_perceptual_hashing(visited_domain_html, ctarget_html) else 0


# parking alert
def evaluate_parka(visited_domain_html, keyphrases):
    num_keyphrases = 0

    for keyphrase in keyphrases:
        if keyphrase in visited_domain_html.lower():
            num_keyphrases += 1

    return 1 if num_keyphrases > 0 else 0


def evaluate_fuzzy_hashing(visited_domain_html, ctarget_html):
    hash1 = ssdeep.hash(visited_domain_html)
    hash2 = ssdeep.hash(ctarget_html)

    return ssdeep.compare(hash1, hash2) >= 25


def evaluate_perceptual_hashing(visited_domain_html, ctarget_html):
    img1_path = hti.screenshot(html_str=visited_domain_html, save_as="visited.jpg")[0]
    img2_path = hti.screenshot(html_str=ctarget_html, save_as="ctarget.jpg")[0]

    img1 = Image.open(img1_path)
    img2 = Image.open(img2_path)

    phash1 = imagehash.phash(img1)
    phash2 = imagehash.phash(img2)

    os.remove(img1_path)
    os.remove(img2_path)

    return phash1 - phash2 < 10