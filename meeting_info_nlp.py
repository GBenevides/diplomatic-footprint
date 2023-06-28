import spacy
import re

import app_statics

# nlp = spacy.load("en_core_web_sm")
nlp = spacy.load("pt_core_news_sm")

# List of strings describing meetings
# meetings = ["- Meeting with Mr. Jacques Chirac, President of France",     "- Departure for Agra to Mumbai", "- Meeting with Mr. Abdul Kalam, President of India", "- Opening of the ""Brazil-India - Sustainable Development: Perspectives and Possibilities"" event"]
meetings = [" - Encontro com o Sr. Jacques Chirac, presidente da República Francesa", " - Partida de Agra  para Mumbai",
            " - Encontro com o sr. Abdul Kalan, presidente da República da Índia",
            "- Abertura  do  Encontro  ""Brasil-Índia  -  Desenvolvimento  Sustentável:    Perspectivas  e Possibilidades"]


def extract_post_country(s):
    pattern = r'(\b\w+\b)(?: da| das| de| do)\s*(.*),?\s*(.*)'
    pattern = r'(\b\w+\b)(?: da| das| de| do)\s+(\b\w+.*\b)'
    match = re.search(pattern, s)
    if match and "Coréia" not in s and not any(
            s == string for string in ["África do Sul", "Costa do Marfim", "CoReia do Sul"]):
        # print("Post/country MATCH:", s, "groups:", match.group(1), "/", match.group(2).strip())
        return match.group(2).strip()
    return s


def find_last_post(line):
    articles = ['a', 'o', 'as', 'os', 'um', 'uns', 'uma', 'umas']
    prepositions = ['de', 'da', 'do', 'em', 'para', 'com', 'por', 'sobre']
    post_detected = []
    tricky_post = ""
    if 'presidente da assembléia' in line.lower():
        tricky_post = 'presidente da assembléia'
    if 'presidente  da  câmara  dos  deputados' in line.lower():
        tricky_post = 'presidente  da  câmara'
    if 'ministro das relações exteriores' in line.lower():
        tricky_post = 'Ministro'
    if 'líder da oposição' in line.lower():
        tricky_post = 'líder da oposição'
    if 'sua santidade' in line.lower():
        tricky_post = 'líder religioso'
    if 'diretor executivo' in line.lower():
        tricky_post = 'ceo'
    if tricky_post:
        post_detected.append(tricky_post)

    words = line.lower().split()
    for word in words:
        if word in list(app_statics.posts_mapping.keys()):  # any(word in posts or word.startswith(p) for p in posts):
            post_detected.append(word)
    return ";".join(post_detected)


def capitalize_monarch(line):
    for keyword in app_statics.royals:
        if keyword.lower() in line.lower():
            authority = keyword.capitalize()
            line = line.replace(keyword, authority)
    return line


def extract_meeting_if_any(meeting_entry):
    line = capitalize_monarch(meeting_entry)
    doc = nlp(line)
    meeting = {"Person": "", "Country": "", "Post": find_last_post(line)}
    persons = []
    countries = []
    last = ''
    for ent in doc.ents:
        # print(ent, ent.label_)
        if (ent.label_ == "PER" and vet_bizarre_person(ent.text)) or rectify_person_false_negative(ent.text):
            if last == 'l' or not last or (
                    last == 'p' and line.index(persons[-1]) + len(persons[-1]) + 1 < line.index(ent.text)):
                persons.append(ent.text)
            else:
                persons[-1] += " " + ent.text
            last = 'p'
        elif (ent.label_ == "LOC" and vet_bizarre_country(ent.text)) or rectify_country_false_negative(ent.text):
            if ent.text not in countries:
                countries.append(extract_post_country(ent.text))
            last = 'l'
    meeting["Person"] = ";".join(persons)
    if not meeting["Person"]:
        return None
    mapped_countries = []
    for c in countries:
        if vet_bizarre_country(c):
            try:
                mapped = app_statics.country_mapping[c]
            except KeyError:
                print("\n\tCountries: ")
                print(countries)
                raise KeyError("Missing key: " + c + " in line: " + line)
            mapped_countries.append(mapped)
    countries = mapped_countries
    meeting["Country"] = ";".join(countries) if mapped_countries else ""
    if meeting["Person"] and not meeting["Country"]:
        last_ditch_attempt = findCountryInStatics(line.lower())
        if last_ditch_attempt:
            mapped = app_statics.country_mapping[last_ditch_attempt]
            meeting["Country"] = mapped

    if (meeting["Person"] and not meeting["Post"] and monarchy(meeting["Person"])) or monarchy(meeting["Post"]):
        meeting["Post"] = "Monarch"

    return meeting if meeting["Person"] and (
                meeting["Country"] or meeting["Post"] or meeting["Person"] in force_names) else None


# TODO  Line triggered:  - Encontro privado com o presidente Alan García !!!

def monarchy(candidate):
    return any(f in candidate.lower() for f in app_statics.royals)


def rectify_person_false_negative(candidate):
    return any(f in candidate for f in
               ["Decker", "Benjamin Netanyahu", "Laurent Gbagbo", "Franco Frattini", "Hu Jintao", "Wen Jiabao",
                "Hifikepunye Pohamba", "Cyril Ramaphosa", "Senhor Andrew Liveris",
                "Laurent Gbagbo", "Manmohan Singh", "Recep Erdogan", "José Mujica",
                "Armando Guebuza", "Lee Myung-bak", "Maurício Funes", "Yasuo Fukuda", "Ban Ki-moon", "Nong Duch Manh",
                "Hifikepunye Pohamba", "Laurent Gbagbo", "Massimo D'Alema", "Recep Tayyip",
                "Gabriele Galatere di Genola", "Presidente de Cabo Verde", "Enrique Peña Nieto"
                   , "Auul Pakir Jainulabdeen Abdul Kalam", "Pedro Pires", "Obiang Nguema Mbasogo"
                   , "Armando Guebuza", "Ren Zhengfei", 'Audiência com Sua Santidade o Papa Francisco', 'Durão Barroso',
                "Emir do Catar  Xeque Tamin bin", "Senadora Lucia Topolansky", "Ban Ki-Moon", "Erick Schmidt"])


# armand de decker
force_names = ["Rupert Murdoch", "Henry Kissinger", "Condoleezza Rice", "Madeleine Albright", "Bill Gates"]


def findCountryInStatics(line):
    lowered = line.lower()
    for key in app_statics.country_mapping.keys():
        if key.lower() in lowered:
            return key
    return None


def rectify_country_false_negative(candidate):
    return any(f in candidate for f in ["Costa do Marfim", "Assembléia Nacional do Vietnã", "Nações Unidas",
                                        "Conselho de Cooperação do Golfo", "Comitê Olímpico Internacional",
                                        "Fórum Econômico  Mundial", "Siemens",
                                        "Cooperação Internacional da Fundação Friedrich Ebert",
                                        "Bill & Melinda Gates Foundation"])


# Returns true if str IS NOT a bizarre country
def vet_bizarre_country(candidate):
    suspect = candidate.lower()
    return len(suspect) > 2 and not any(f in suspect for f in
                                        ["recepção", "audiência", "chanceler", "g-5", "brics", "secretário-geral",
                                         "posse", "estado", "estados associados", "mercosul", "conferência", "reunião",
                                         "armand", "encontro", "saudação", "aprobras", "cerimônia", "senado", "câmara",
                                         "alto nível", "sua santidade",
                                         "governo da", "presidente da grande assembléia nacional da turquia", "jantar",
                                         "almoço", "finanças do", "agility", 'relações exteriores', "trabalho",
                                         "américa", "chairman",
                                         "indústrias", 'telefônica', "presidenta", 'diretor-geral', 'ex-presidente da república portuguesa'])


def vet_bizarre_person(candidate):
    suspect = candidate.lower()
    return len(suspect) > 2 and not any(f == suspect for f in ["suas majestades", "presidenta da república",'rainha da dinamarca',
                                                               "linkspartei", "dinamarca", "rei da bélgica", "presidente da siemens",
                                                               "audiência", 'coca-cola',"emir do catar", "presidente de cuba"]) \
           and suspect not in ["dra"]


"""
extract_meeting_if_any(meetings[0])
extract_meeting_if_any(meetings[1])
extract_meeting_if_any(meetings[2])
extract_meeting_if_any(meetings[3])
"""
