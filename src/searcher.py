import httpx, base64, re
from datetime import datetime
from fake_useragent import UserAgent

def google_search(query):
	search_results = []
	dym = ""

	ua = UserAgent()
	headers = { 'User-Agent': ua.random }
	
	# socs è un cookie codificato in base64 che indicata la data di conferma dei cookie di google, ha durata 13 mesi
	socs_bytes = b"\x08\x02\x12\x1c\x08\x02\x12\x12gws_" + datetime.now().strftime('%Y%m%d').encode('utf-8') + b"-0_RC6\x1a\x02it \x01\x1a\x06\x08\x80\xf4\xf8\xab\x06"
	socs = base64.b64encode(socs_bytes).decode('utf-8')
	cookies = { 'SOCS': socs }

	url = f"https://www.google.com/search?q={query}&num=10"

	r = httpx.get(url, headers=headers, cookies=cookies, follow_redirects=True)
	data = r.text
	divs = re.split('>(http(s)?:\/\/)', data)
	for div in divs:
		if div is not None and "doctype" not in div:
			if "cite" in div:
				url = re.split('</cite', div)[0].replace("www.", "").replace(r"\/.*", "")
				if "<" not in url and ">" not in url and url not in search_results:
					search_results.append(url)
			if "span" in div:
				url = re.split('<span', div)[0].replace("www.", "").replace(r"\/.*", "")
				if "<" not in url and ">" not in url and url not in search_results:
					search_results.append(url)

	# get DYM
	dym_patterns = [
		r"Forse cercavi:.*?q=",
		r"Risultati relativi a.*?q=",
		r"Sono inclusi i risultati per.*?q=",
		r"Did you mean:.*?q=",
		r"Showing results for.*?q=",
		r"Including results for.*?q="
	]

	for pattern in dym_patterns:
		if re.search(pattern, data):
			dym = re.split(pattern, data)[1].split("&amp")[0]
			break

	return { "search_results": search_results, "dym": dym }

def bing_search(query):
	return 0

