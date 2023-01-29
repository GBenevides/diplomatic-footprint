import spacy
import re

import app_statics

nlp = spacy.load("en_core_web_sm")
nlp = spacy.load("pt_core_news_sm")

# List of strings describing meetings
# meetings = ["- Meeting with Mr. Jacques Chirac, President of France",     "- Departure for Agra to Mumbai", "- Meeting with Mr. Abdul Kalam, President of India", "- Opening of the ""Brazil-India - Sustainable Development: Perspectives and Possibilities"" event"]
meetings = [" - Encontro com o Sr. Jacques Chirac, presidente da República Francesa", " - Partida de Agra  para Mumbai",
            " - Encontro com o sr. Abdul Kalan, presidente da República da Índia",
            "- Abertura  do  Encontro  ""Brasil-Índia  -  Desenvolvimento  Sustentável:    Perspectivas  e Possibilidades"]


def extract_post_country(s):
    pattern = r'(\b\w+\b)(?: da| de| do)\s*(.*),?\s*(.*)'
    match = re.search(pattern, s)
    if match and "Coréia" not in s and s != "África do Sul":
        # print("Post/country MATCH:", s, "groups:", match.group(1), "/", match.group(2).strip())
        return match.group(2).strip()
    return s


def find_last_post(line):
    articles = ['a', 'o', 'as', 'os', 'um', 'uns', 'uma', 'umas']
    prepositions = ['de', 'da', 'do', 'em', 'para', 'com', 'por', 'sobre']
    if 'presidente da assembléia' in line.lower():
        return 'presidente da assembléia'
    if 'presidente  da  câmara  dos  deputados' in line.lower():
        return 'presidente  da  câmara'

    posts = ['presidente', 'presidenta', 'primeiro-ministro', 'primeira-ministra', 'chanceler',
             'presidentes', 'vice-presidente', 'vice-presidenta', 'secretário-geral']

    words = line.lower().split()
    post_detected = []
    for word in words:
        if word in posts:  # any(word in posts or word.startswith(p) for p in posts):
            post_detected.append(word)
    return ";".join(post_detected)


def extract_meeting_if_any(line):
    doc = nlp(line)
    meeting = {"Person": "", "Country": "", "Post": find_last_post(line)}
    persons = []
    countries = []
    last = ''
    for ent in doc.ents:
        # print(ent, ent.label_)
        if ent.label_ == "PER" or rectify_person_false_negative(ent.text):
            if last == 'l' or not last:
                persons.append(ent.text)
            else:
                persons[-1] += " " + ent.text
            last = 'p'
        elif (ent.label_ == "LOC" and vet_bizarre_country(ent.text)) or rectify_country_false_negative(ent.text):
            if ent.text not in countries:
                countries.append(extract_post_country(ent.text))
            last = 'l'
    meeting["Person"] = ";".join(persons)
    meeting["Country"] = ";".join(countries) if all(vet_bizarre_country(c) for c in countries) else ""
    if meeting["Person"] and not meeting["Country"]:
        last_ditch_attempt = findCountryInStatics(line.lower())
        if last_ditch_attempt: meeting["Country"] = last_ditch_attempt

    return meeting if meeting["Person"] and (meeting["Country"] or meeting["Post"]) else None


# TODO  Line triggered:  - Encontro privado com o presidente Alan García !!!
def rectify_person_false_negative(candidate):
    return any(f in candidate for f in
               ["Franco Frattini", "Hu Jintao", "Wen Jiabao", "Hifikepunye Pohamba", "Laurent Gbagbo", "Manmohan Singh",
                "Armando Guebuza", "Lee Myung-bak", "Yasuo Fukuda", "Ban Ki-moon", "Nong Duch Manh"])


def findCountryInStatics(line):
    lowered = line.lower()
    for key in app_statics.country_mapping.keys():
        if key.lower() in lowered:
            return key
    return None


def rectify_country_false_negative(candidate):
    return any(f in candidate for f in ["Assembléia Nacional do Vietnã", "Nações Unidas"])


# Returns true if str IS NOT a bizarre country
def vet_bizarre_country(candidate):
    suspect = candidate.lower()
    return not any(f in suspect for f in ["reunião", "encontro", "aprobras", "cerimônia"])


"""
extract_meeting_if_any(meetings[0])
extract_meeting_if_any(meetings[1])
extract_meeting_if_any(meetings[2])
extract_meeting_if_any(meetings[3])
"""
