from urllib.parse import urlparse
from src.ecm import *
from src.result import Result
from src.avm import *
from src.searcher import *
from src.models import *
import re, os, httpx
from datetime import datetime, timedelta

def get_list_from(filename):
	path = os.path.join(os.path.abspath(os.path.dirname(__file__)), '../static/res')
	with open(f"{path}/{filename}", 'r') as file:
		rows = file.readlines()

	domains = [row.strip() for row in rows]
	return domains


top_domains = get_list_from("topdomains.txt")
blackbook = get_list_from("blackbook.txt")
keyphrases = get_list_from("keyphrases_domain_parking.txt")


def analyze_domain(curr_user, input_domain, no_cache):
	visited_domain_response = get_response_from_url(input_domain)
	if visited_domain_response == "Unreachable domain!":
		raise Exception("Unreachable domain!")
	
	parsed_url = urlparse(visited_domain_response.url.__str__())
	visited_domain = parsed_url.hostname.replace("www.", "")
	visited_domain_html = visited_domain_response.text

	user_domains = [domain.domain_name for domain in curr_user.domains]
	verified_domains = top_domains + user_domains

	# check if domain is in blackbook
	for malware_domain in blackbook:
		if malware_domain == input_domain or malware_domain == visited_domain:
			return { "target": "", "analysis": Result.Malware.name, "other_targets": [], "evaluated_on": datetime.now().strftime("%Y/%m/%d") }

	analysis = Result.Unknown
	ctargets = []

	# looking for similar domain
	for verified_domain in verified_domains:
		if verified_domain == input_domain or verified_domain == visited_domain:
			return { "target": "", "analysis": Result.NotTypo.name, "other_targets": [], "evaluated_on": datetime.now().strftime("%Y/%m/%d") }
		
		dl_distance = damerau_levenshtein_distance(verified_domain, input_domain)
		if dl_distance == 1:
			analysis = Result.ProbablyTypo
			ctargets.append(verified_domain)


	# check whether the domain has already been analyzed by someone else (cache checking)
	domain = Domain.query.filter_by(domain_name=input_domain).first()
	if domain and domain.evaluated_on and not no_cache:
		evaluated_within_30_days = False
		evaluation_date = domain.evaluated_on
			
		if evaluation_date:
			diff = datetime.now() - evaluation_date
			evaluated_within_30_days = diff <= timedelta(days=30)
		
		# if one of the user-verified domains is considered as ctarget I don't check the cache
		ctarget_in_user_list = False
		for ctarget in ctargets:
			if any(ctarget == user_domain.domain_name for user_domain in curr_user.domains):
				ctarget_in_user_list = True
				break

		if not ctarget_in_user_list and evaluated_within_30_days:
			return { "target": domain.target, "analysis": domain.analysis, "other_targets": [d for d in domain.other_targets.split(';') if d], "evaluated_on": evaluation_date.strftime("%Y/%m/%d") }

	# deepen ProbablyTypo
	target = ""
	other_targets = []
	if analysis == Result.ProbablyTypo:
		gsearch = google_search(input_domain)

		parka = evaluate_parka(visited_domain_html, keyphrases)

		curr_analysis = Result.Unknown
		for ctarget in ctargets:
			ctarget_domain_response = get_response_from_url(ctarget)

			t10a = evaluate_t10a(input_domain, ctarget, gsearch["search_results"])
			dyma = evaluate_dyma(ctarget, gsearch["dym"])
			pha = evaluate_pha(visited_domain_html, ctarget_domain_response.text)

			print(t10a, dyma, pha, parka)
			alert_value = t10a + dyma + pha + parka

			if alert_value == -1:
				ctarget_analysis = Result.ProbablyNotTypo
			elif alert_value == 0:
				ctarget_analysis = Result.ProbablyTypo
			else:
				if pha == 1:
					ctarget_analysis = Result.TypoPhishing
				else:
					ctarget_analysis = Result.Typo

			if ctarget_analysis.value > curr_analysis.value:
				curr_analysis = ctarget_analysis
				target = ctarget

		analysis = curr_analysis
		other_targets = [ctarget for ctarget in ctargets if ctarget != target]


	# save evaluation
	evaluation_date = datetime.now()
	if domain:
		if not any(user_domain.domain_name == input_domain or target == user_domain.domain_name for user_domain in curr_user.domains):
			domain.target = target
			domain.analysis = analysis.name
			domain.other_targets = ';'.join(other_targets)
			domain.evaluated_on = evaluation_date

			db.session.commit()
	else:
		if not any(user_domain.domain_name == input_domain or target == user_domain.domain_name for user_domain in curr_user.domains):
			new_domain = Domain(domain_name=input_domain, target=target, analysis=analysis.name, other_targets=';'.join(other_targets), evaluated_on = evaluation_date)
			db.session.add(new_domain)
			db.session.commit()

	return { "target": target, "analysis": analysis.name, "other_targets": other_targets, "evaluated_on": evaluation_date.strftime("%Y/%m/%d")  }


def is_email_valid(email):
	email_regex = re.compile(r'([A-Za-z0-9]+[.-_])*[A-Za-z0-9]+@[A-Za-z0-9-]+(\.[A-Z|a-z]{2,})+')

	if re.fullmatch(email_regex, email):
		return True
	
	return False


def is_domain_valid(domain):
	domain_regex = re.compile(r'^(?!www)([-a-zA-Z0-9@:%._\+~#=]+\.)+[a-z]{2,6}$')

	if re.fullmatch(domain_regex, domain):
		return True
	
	return False


def is_top_domain(domain):
	return domain in top_domains


def get_response_from_url(domain):
	try:
		response = httpx.get(f"https://{domain}", follow_redirects=True, timeout=5)
	except Exception as e:
		try:
			response = httpx.get(f"http://{domain}", follow_redirects=True, timeout=5)
		except Exception as e:
			return "Unreachable domain!"
		
	return response