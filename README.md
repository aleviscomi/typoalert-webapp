# TypoAlert
_(WebApp Version) Thesis project for the **Master's Degree in Computer Engineering (Cyber Security)** @ **University of Calabria**_

![Logo](static/img/logo.png)

TypoAlert is a Chrome extension to detect typosquatted domains. It constantly monitors the user's navigation to detect typosquatting attacks and promptly notify them. In practice, when the user lands on a typosquatted domain, TypoAlert immediately draws their attention. Additionally, it also allows for configuring specific preferences to adapt to the individual user's browsing habits.


## Key Components

- **BlackBook:** A continuously updated historical [blacklist](https://github.com/stamparm/blackbook) containing numerous domains known for their malicious nature.

- **Top Domains Repository (TDR):** An archive of reliable domains, consisting of the top 50 globally visited domains, as well as the top 50 domains in each individual nation.

- **User Domains Repository: (UDR):** Similar to the TDR, it represents an archive of reliable domains, but initially empty and can be customized by the user according to their preferences.

- **Edit-Distance Computation Module (ECM):** This module performs lexical analysis by calculating the Damearu-Levenshtein (DL) distance between the input domain and those present in the two repositories. If a domain in one of the repositories has a DL-distance of 1 from the input domain, a possible typosquatting situation is flagged, and that domain is considered as a potential target.

- **Alerts Verification Module (AVM):** This module is based on the analysis of four indicators to confirm or refute a potential typosquatting situation flagged by the ECM. These indicators encompass the ***Top 10 Alert***, which leverages search engine results (Google or Bing), the ***Did You Mean Alert***, utilizing search engine "DYM" mechanisms, the ***Phishing Alert***, employing fuzzy and perceptual hashing, and the ***Parking Alert***, which identifies keyphrases commonly associated with parked pages.


## Usage

First, install requirements:

```bash
pip install -r requirements.txt
```

Then, run the app:

```bash
python3 app.py
```

and visit <a href="http://localhost:5000">http://localhost:5000</a>