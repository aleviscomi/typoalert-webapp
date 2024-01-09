def damerau_levenshtein_distance(str1, str2):
    len_str1 = len(str1)
    len_str2 = len(str2)

    d = [[0] * (len_str2 + 1) for _ in range(len_str1 + 1)]

    for i in range(len_str1 + 1):
        d[i][0] = i

    for j in range(len_str2 + 1):
        d[0][j] = j

    for i in range(1, len_str1 + 1):
        for j in range(1, len_str2 + 1):
            cost = 0 if str1[i - 1] == str2[j - 1] else 1
            d[i][j] = min(
                d[i - 1][j] + 1,       # insertion
                d[i][j - 1] + 1,       # deletion
                d[i - 1][j - 1] + cost  # substitution
            )

            if i > 1 and j > 1 and str1[i - 1] == str2[j - 2] and str1[i - 2] == str2[j - 1]:
                d[i][j] = min(d[i][j], d[i - 2][j - 2] + cost)  # transposition

    return d[len_str1][len_str2]


def check_tld_difference(domain1, domain2):
    return 0