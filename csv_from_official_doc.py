from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage
from io import StringIO
import csv
import re
from collections import OrderedDict

import app_statics
from app_statics import *
import sys
import meeting_info_nlp
import PyPDF2
import json


def mk_degenerate_cases(year):
    cases = []
    if year == "2007":
        jamaica = blank_visit_entry(year)
        jamaica["Country"] = "Jamaica"
        jamaica["City/region"] = "Kingston"
        jamaica["Overview"] = jamaica_visit_2007_overview
        jamaica["Period"] = "9 de Agosto"
        jamaica["Host"] = ["Host"]
        cases.append(jamaica)
    return cases


def generate_csv(path, year, csv_prefix, verbose=False, pdfMiner=False, rearrange=True, testMode=False):
    pdf_text = convert_pdf_to_txt_pdfminer(path) if pdfMiner else convert_pdf_to_txt_pypdf2(path)
    raw_visits = visits_from_text(pdf_text, year)
    if verbose:
        for entry in raw_visits: print(entry)
    results = rearrange_state_visits(raw_visits) if rearrange else (raw_visits, 0)
    visits = results[0]
    nb_meetings = results[1]
    degenerate_cases = mk_degenerate_cases(year)
    visits = visits + degenerate_cases
    nb_visits = len(visits)
    if verbose:
        print("Number of visits", nb_visits)

    # with open('data/' + csv_prefix + "-" + year + '.csv', mode='w') as csv_file:
    #     writer = csv.DictWriter(csv_file, fieldnames=data_visit_columns)
    #     writer.writeheader()
    #     for visit in visits:
    #         if verbose: print("Writing to csv: ", visit["City/region"], ",", visit["Country"])
    #         writer.writerow(visit)
    if not testMode:
        with open('data/' + csv_prefix + "-" + year + '.json', 'w') as jsonFile:
            json.dump(visits, jsonFile, indent=4)
    return nb_visits, nb_meetings


def convert_pdf_to_txt_pypdf2(path):
    with open(path, 'rb') as f:
        pdf = PyPDF2.PdfReader(f)
        text = ""
        for i in range(0, len(pdf.pages)):
            text += pdf.pages[i].extract_text()
    return text


def convert_pdf_to_txt_pdfminer(path):
    rsrcmgr = PDFResourceManager()
    retstr = StringIO()
    laparams = LAParams()
    device = TextConverter(rsrcmgr, retstr, laparams=laparams)
    fp = open(path, 'rb')
    interpreter = PDFPageInterpreter(rsrcmgr, device)
    password = ""
    maxpages = 0
    caching = True
    pagenos = set()
    for page in PDFPage.get_pages(fp, pagenos, maxpages=maxpages, password=password, caching=caching,
                                  check_extractable=True):
        interpreter.process_page(page)
    text = retstr.getvalue()
    fp.close()
    device.close()
    retstr.close()
    return text


unwanted_lines = ["", "Presidência da República", "Casa Civil", "Secretaria Especial de Comunicação Social",
                  "Viagens Internacionais", "Viagens Internacionais do Presidente da República",
                  "Secretaria de Comunicação Social", "Secretaria de Imprensa",
                  'Viagens Internacionais do Presidente da República/2008',
                  '(Tanzânia), Lusaca (Zâmbia), Johannesburgo (África do Sul)',
                  'Johanesburgo (África do Sul) e Luanda (Angola)',
                  'Luanda / Angola', '- Chegada ao Aeroporto de Luanda / Angola',
                  'Atualizado em 18/12/2007', 'Madri',
                  'Primeiro Secretário-Geral da Unasul, Néstor Carlos Kirchner']


def same_visit(visit, father_visit):
    numbers_patten = re.compile(r'\d+')
    father_day = max(int(x) for x in re.findall(numbers_patten, father_visit["Period"]))
    father_month = father_visit["Period"].split()[-1].lower()
    father_month_index = months.index(father_month)
    visit_day = min(int(x) for x in re.findall(numbers_patten, visit["Period"]))
    visit_month = visit["Period"].split()[-1].lower()
    visit_month_index = months.index(visit_month)
    same_country = visit["Country"] in father_visit["Country"]
    if abs(visit_month_index - father_month_index) > 1:  # more than a month apart, no way
        same = False
    elif visit_month_index == father_month_index:
        same = visit_day - father_day <= 3 and same_country  # It must be the same visit if it's the next day,
        # and the same country
    else:  # One month after the other, either father is 31 or 28 for february
        same = (father_day == 29 or father_day == 30 or father_day == 31 or (
                father_day == 28 and father_month_index == 1)) \
               and visit_day == 1 and same_country
    return same


def skip_prohibitive_visits(visit):  # unstructured pdf :(
    overview = visit["Overview"]
    prohibitive = ['Partida para San Salvador/El Salvador', 'Jamaica Broilers Group']
    for p in prohibitive:
        if any(p in s for s in overview):
            return True
    return False


def rearrange_state_visits(visits):
    rearranged = []
    father_visit = visits[0]
    for visit in visits[1:]:
        if skip_prohibitive_visits(visit):
            continue
        if visit["Period"] and not same_visit(visit, father_visit):
            if father_visit != {}:
                append_visits(father_visit, rearranged)
            father_visit = visit
        else:
            father_visit["Overview"].append(" - [" + visit["City/region"] + "]")
            father_visit["Overview"] += (visit["Overview"])
    append_visits(father_visit, rearranged) # Last one
    counter = 0
    previous = None  # avoid double host calculation
    all_inconsistent_posts = []
    for v in rearranged:
        #print(v["Country"], v["Period"])
        if previous is None or (v["Period"].lower() != previous["Period"].lower()):
            # Looking for potential hosts...
            # enumeratedPoints = enumerate(v["Overview"])
            assert type(v["Overview"]) == list
            for next_point in v["Overview"]:
                next_point_strip = next_point.strip()
                post_treated = brutal_replace_if_any(next_point_strip, v["year"])
                positive_trigger = any(
                    t in post_treated.lower() for t in app_statics.triggers + list(app_statics.posts_mapping.keys()))
                negative_trigger = any(t in post_treated.lower() for t in app_statics.negative_triggers)
                if positive_trigger and not negative_trigger:
                    # print("Line triggered:", post_treated, "date:", v["Period"])
                    meeting_if_any = meeting_info_nlp.extract_meeting_if_any(post_treated)
                    if meeting_if_any:
                        mapped_meeting, incoming_inconsistent = map_name(meeting_if_any, v["year"])
                        if len(mapped_meeting) > 0:
                            #print("Meeting --> ", mapped_meeting, "   ---   ", v["Period"], "   ---   ", next_point)
                            v["Host"].append(mapped_meeting)
                            all_inconsistent_posts += incoming_inconsistent
                            counter += 1
        previous = v

        v["Overview"] = "\n".join(v["Overview"])
        # More cleaning...
        v["Overview"] = v["Overview"].replace("–", "-")
        # Translate overview now ?
        v["Period"] = format_location(v["Period"])
    print("Inconsistent posts:\n", list(OrderedDict.fromkeys(all_inconsistent_posts)))
    print("Total meetings:", counter)
    # print(app_statics.leaders_mapping)
    return rearranged, counter


def map_name(meeting, year):
    try:
        # raw_name, country, post = entry['Person'], entry['Country'], entry['Post']
        raw_name = meeting['Person']
        mapped = []
        inconsistent_posts = []
        for i, indiv_name in enumerate(raw_name.split(app_statics.separator_char)):
            code_name = app_statics.leaders_mapping_codes[indiv_name]
            if code_name is None:
                continue
            indiv_mapped = app_statics.leaders_mapping[code_name]
            posts_split_if_any = meeting['Post'].split(app_statics.separator_char)
            if i < len(posts_split_if_any):
                post_pre_split = posts_split_if_any[i]
                entry_post = app_statics.posts_mapping[post_pre_split] if post_pre_split else app_statics.empty_post
            else:
                entry_post = ''
            if code_name not in app_statics.account_post_inconsistency[year] and entry_post not in indiv_mapped[
                'posts']:
                print("Inconsistent post in:", code_name, '/', raw_name, '-->', entry_post, ' / ',
                      indiv_mapped['posts'])
                inconsistent_posts.append(code_name)
            mapped.append(indiv_mapped)
        return mapped, inconsistent_posts
    except KeyError:
        print("Error in meeting:", meeting)
        print("\n\tMissing in figure dict... Suggestion:")
        entry_post = app_statics.posts_mapping[meeting['Post']]
        new_entry = make_person_entry(meeting['Person'], meeting['Country'], entry_post)
        person_upper = meeting["Person"][0:2].upper()
        code_key_sugg = person_upper + "1"
        print('"' + code_key_sugg + '"', ":", new_entry, '--->', "'" + new_entry['figure'] + "'", ":",
              "'" + code_key_sugg + "'", ",")
        existing_codes = [element for element in app_statics.leaders_mapping.keys() if
                    element[0:2] == meeting["Person"][0:2].upper()]
        print("Existing entries:")
        for code in existing_codes:
            print(code, app_statics.leaders_mapping[code]['figure'])
        raise KeyError("Missing key: " + meeting['Person'], meeting)


def make_person_entry(name, country, post):
    return {"figure": name, "country": country, "posts": [post]}


def append_visits(father_visit, rearranged_list):
    country = father_visit["Country"]
    country_separator = ";"
    if country_separator in country:  # Generate different visits with exact same content
        sub_visits = break_up_multiple_countries_visits(father_visit)
        rearranged_list += sub_visits  # Extend list
    else:
        rearranged_list.append(father_visit)


def break_up_multiple_countries_visits(father_visit):
    sub_visits = [father_visit]
    country = father_visit["Country"]
    countries = country.split(";")
    father_visit["Country"] = countries[0]
    for c in countries[1:]:
        clone = father_visit.copy()  # Clone content
        clone["Country"] = c
        sub_visits.append(clone)
    return sub_visits


def blank_visit_entry(year):
    return {"year": year, "Overview": [], "Host": [], "Period": "", "Country": ""}


def format_location(loc):
    articles = ["De", "Do", "E", "Da", "Das", "Del", "A"]
    loc = loc.strip().strip("()")
    loc = loc.title()
    for prep in articles:
        prep_spaces = f" {prep} "
        prep_spaces_lower = f" {prep.lower()} "
        loc = loc.replace(prep_spaces, prep_spaces_lower)
    return loc


def check_no_prohibitive_locs(line):
    prohibitive_terms = ["Celac", "Aprobras", "Sica", "Unasul", "Cedeao", "Chegada a Pequim"]
    for term in prohibitive_terms:
        if term in line: return False
    return True


def brutal_replace_if_any(raw, year):  # Sadly, pdf too inconsistent
    replacement = raw
    replace_lines = {
        'São Salvador (El Salvador) e Havana (Cuba)': ['Salvadorcuba (Salv Cuba)', '2008'],
        'Punta Arenas (Chile) Estação Antártica Comandante Ferraz': ['Punta Arenas (Chile)', '2008'],
        'Punta Arenas (Chile ) Estação Antártica Comandante Ferraz': ['Punta Arenas (Chile)', '2008'],
        'Oiapoque, Macapá (AP)  e Guiana Francesa': ['Oiapoque (França)', '2008'],
        'Oiapoque, Macapá (AP) e Guiana Francesa': ['Oiapoque (França)', '2008'],
        'Paris (França) e Londres (Inglaterra)': ['Parislondres (France Eng)', '2009'],
        'San Salvador (El Salvador) e Cidade de Guatemala (Guatemala)': ["Salvadorguate (Salv Guate)", '2009'],
        'Lisboa (Portugal) e Kiev (Ucrânia)': ['Kiev (Ucrânia)', '2009'],
        'Reunião com o presidente da Coreia do Sul, Lee Myung-bak': ['- Reunião com o presidente da Coreia do Sul, '
                                                                     'Lee Myung-bak', '2010'],
        'Porto Príncipe (Haiti) e São Salvador (El Salvador)': ['Portsalv (HaitSalv)', "2008"],
        'Montevidéu (Uruguai) e Santiago (Chile)': ["Montiago (Uruchil)", "2010"],
        'Jerusalém (Israel), Belém (Palestina), Ramalá (Cisjordânia) e Amã (Jordânia)': ["Jerberama (Ispalcisjor)",
                                                                                         "2010"],
        'Buenos Aires (Argentina) e Montevidéu (Uruguai)': ["Buenvideu (Arguay)", "2010"],
        'Ilha do Sal (Cabo Verde), Malabo (Guiné Equatorial), Nairóbi (Quênia), Dar es Salaam': [
            'Ilhamanadarlujo (Caboguique Tanzamafr)', "2010"],
        'Rivera (Uruguai) e Assunção (Paraguai)': ["Rivasu (Urupara)", "2010"],
        'Caracas (Venezuela) e Bogotá (Colômbia)': ["Carabogo (Venelombia)", "2010"],
        'Ouagadougou/Burkina Faso e  Brazzaville/Congo (África)': ['Ouagabraza (Burcongo)', "2007"],
        'NOVA DELHI, AGRA, MUMBAI (Índia)': ['Dehliagramum (Índia)', "2004"],
        'SANTA CRUZ DE LA SIERRA (Bolívia)': ["Santacsi (Bolívia)", "2004"],
        'SÃO TOMÉ E PRÍNCIPE': ['Saotome (Saotomeeprincipe)', "2004"],
        "CIUDAD GUAYANA (Venezuela)": ["Ciudaguyana (Venezuela)", "2005"],
        "ROMA (Itália)": ["Roma (Italia)", "2005"],
        "ACRA (Gana)": ["Acra (Gana)", "2005"],
        "- Cerimônia de abertura de encontro empresar ial, com a presença do presidente de El Salvador, Elias Antonio Saca": [
            "", "2008"],
        "- Reunião com os Presidentes dos países membros do Sistema de Integração Centro- Americana (Sica)": ["",
                                                                                                              "2008"],
        "- Reunião com os Presidentes dos países membros do Sistema de Integração Centro- Graduados no Brasil (Aprobras) Salvador, Elias Antonio Saca Americana (Sica)": [
            "", "2008"],
        "- Encontro com o presidente de Cote d'Ivoire, Laurent Gbagbo": [
            "- Encontro com o presidente da Costa do Marfim, Laurent Gbagbo", "2008"],
        "- Encontro com o Presidente da República italiana, Giorgio Napolitano": [
            "- Encontro com o Presidente da Italia, Giorgio Napolitano", "2008"],
        "- Encontro com Sua Santidade o Papa Bento XVI": ["- Encontro com chefe do Vaticano, o Papa Bento XVI", "2008"],
        "- Encontro com a Presidenta da República Argentina, Cristina Fernández de Kirchner": [
            "- Encontro com a presidenta da Argentina, Cristina Fernández de Kirchner", "2008"],
        "- Audiência ao senhor Massimo D'Alema": ["- Primeiro-ministro da Italia, Massimo D'Alema", "2008"]
    }
    if raw in replace_lines.keys() and replace_lines[raw][1] == year:
        replacement = replace_lines[raw][0]
    return replacement


def rectify_loc(line, current_country):
    replacement = line
    replace_lines = {
        '29 de março': ['Período: 29 de março', 'Venezuela'],
        '07 de abril': ['Período: 07 de abril', 'Italy'],
        '10 de abril': ['Período: 10 de abril', 'Cameroon'],
        '11 de abril': ['Período: 11 de abril', 'Nigeria'],
        '12 de abril': ['Período: 12 de abril', 'Ghana'],
        '13 de abril': ['Período: 13 de abril', 'Senegal']
    }
    if line in replace_lines.keys() and current_country == replace_lines[line][1]:
        replacement = replace_lines[line][0]
    return replacement


def last_sanity_check_for_month(line):
    return any([word for word in line.lower().split() if len(word) >= 4 and word not in months])


def visits_from_text(pdf_text, year):
    # Regular expressions to match the different parts in the official pdf
    month_re = re.compile(
        r"(Janeiro|Fevereiro|Março|Abril|Maio|Junho|Julho|Agosto|Setembro|Outubro|Novembro|Dezembro)\s*$",
        re.IGNORECASE)
    month__colon_re = re.compile(
        r"(Janeiro|Fevereiro|Março|Abril|Maio|Junho|Julho|Agosto|Setembro|Outubro|Novembro|Dezembro):\s*$",
        re.IGNORECASE)
    location_re = re.compile(r"^([\w\s]+)\s+\(([\w\s]+)\)")  # Parenthesis: Lima (Peru)
    location_re = re.compile(r"^([\w\s]+)\s+\(([\w\s]+[a-z]+[\w\s]+)\)")  # Same, but at least 1 lower case in country
    location_re = re.compile(r"^([\w\s]+)\s+\(([\w\s]+[a-z]+[\w\s]+|EUA)\)")  # Same, but accept EUA
    location_re = re.compile(r"^([A-Z][\w\s]+)\s+\(([\w\s]+[a-z]+[\w\s]+|EUA)\)")  # Same, but first letter is upercase
    location_re = re.compile(r"^([A-Z][\w\s]+)\s+\(([\w\s]+[a-z]+[\w\s]+|EUA)\)$")  # Same, but ends after ()

    location2_re = re.compile(r"^(?!-)\s*([\w\s]+)/([\w\s]+)")  # Slash: Lima/Peru
    vowel_check = re.compile(r"[aeiouAEIOU]")  # Matches if there is a vowel
    period_re = re.compile(r"Período:\s+(.+)")
    period_re = re.compile(r"Período:?\s+(.+)")  # ":" optional

    overview_re = re.compile(r"(-\s.+)")
    updated_re = re.compile(r"^(?!Atualizado).*(?<!\d{2}/\d{2}/\d{4}$)")

    state_visits = []
    awkward_locs = ['Pequim, Sanya, Boao e Xian (China)', 'VALPARAÍSO  e VIÑA DEL MAR (Chile)',
                    'GABORONE (Botsuana) e JOHANESBURGO (África do Sul)', 'SANTIAGO (Chile) e BUENOS AIRES (Argentina)',
                    'Tegucigalpa (HONDURAS) e  Manágua  (NICARÁGUA)', 'Díli (Timor-Leste)',
                    'São Salvador (El Salvador) e Havana (Cuba)',
                    'Roma e L’Aquila (Itália)']
    malformed_periods = {'Período: 15 de setembro de 2008': "15 de setembro"}
    missing_period = "BISSAU (Guiné-Bissau)"
    correct_missing_period = "Bissau (Guiné Bissau)\nPeríodo: 13 de abril\n"
    if year == "2005":
        pdf_text = pdf_text.replace(missing_period, correct_missing_period)
    last_is_overview = False
    current_visit = blank_visit_entry(year)
    force_overview = ['Encontro com a imprensa', 'Reunião com o presidente da Coreia do Sul, Lee Myung-bak',
                      'Presidente da Huawei, Ren Zhengfei', 'Foto oficial da XIV Cúpula do G-1',
                      'Sessão de abertura da XIV Cúpula do G-1', 'Partida para Madri',
                      'Inauguração de estátua em homenagem ao ex-Presidente da Nação Argentina e']
    # Iterate over the lines in the pdf text
    for line in pdf_text.split("\n"):
        line = basic_prepare_line(line, year)
        # Check if the line matches a header or month, it should be ignored
        if line in unwanted_lines:
            continue
        # Check if the line matches a period
        month_match = month_re.search(line)
        if year == "2005" and month_match:
            line = rectify_loc(line, current_visit["Country"])
        period_match = period_re.search(line)
        if period_match and (month_match or line in malformed_periods.keys()):
            current_visit["Period"] = malformed_periods[line] \
                if line in malformed_periods.keys() else period_match.group(1)
            continue
        if month_match and not overview_re.search(line) and not last_sanity_check_for_month(line):
            continue
        # Check if the line matches a location AND has at least one vowel
        replaced_line = brutal_replace_if_any(line, year)
        location_match = location_re.search(replaced_line)
        location_match2 = location2_re.search(replaced_line)
        awkward_match = re.search(r"([\w\s,]*)(\(.*\))", replaced_line) if replaced_line in awkward_locs else None
        if location_match or location_match2 or awkward_match:
            loc = location_match2 if location_match2 else location_match if location_match else awkward_match
            loc_country = format_location(loc.group(2))
            loc_region = format_location(loc.group(1))
            if re.search(vowel_check, loc_country) and (len(loc_region.split()) < 5 or awkward_match) \
                    and check_no_prohibitive_locs(replaced_line):  # and loc_country not in current_visit["Country"]:
                # We found a new visit, let's save the current one and start a new one :)
                if current_visit != blank_visit_entry(year):
                    state_visits.append(current_visit)
                    current_visit = blank_visit_entry(year)  # Start new one!
                    last_is_overview = False
                try:
                    city = city_mapping[loc_region]
                    country = country_mapping[loc_country]
                except KeyError:
                    try:
                        city = city_mapping[loc_country]
                        country = country_mapping[loc_region]
                    except KeyError:
                        raise KeyError("Missing key:", loc_country, loc_region, "Year", year)
                current_visit["City/region"] = f"{city}"
                current_visit["Country"] = f"{country}"
                continue
        # Check if the line matches an overview , that is, starts with "-"
        overview_match = overview_re.search(line)
        if overview_match or line in force_overview:
            # if not current_visit["Overview"].endswith("\n"): current_visit["Overview"] += "\n"
            #            current_visit["Overview"] += "\n" + overview_match.group(1)
            line_to_append = " - " + line.lstrip("-").strip()
            current_visit["Overview"].append(line_to_append)
            last_is_overview = True
            continue
        # Sometimes the line will be the continuation of the line before
        if last_is_overview and line and line not in unwanted_lines and updated_re.search(line) and len(
                line) > 1 and not month__colon_re.search(line):
            # if not current_visit["Overview"].endswith("\n"): current_visit["Overview"] += "\n"
            prefix = " "
            if line.startswith("-"):  # or line[0].isupper(), but then how do we know it isn't a name ? :'(
                line = line.lstrip("-")
                prefix = ' - '
                current_visit["Overview"].append(prefix + line)
            else:
                current_visit["Overview"][-1] += prefix + line
            continue

    # We do not forget to append the last visit !
    state_visits.append(current_visit)
    return state_visits


def basic_prepare_line(line, year):
    prep_line = line.strip().rstrip("/ 2005")
    if year == "2015":
        prep_line = prep_line.split(";")[0]
    return prep_line.replace("Caribe - União Européia", "Caribe-União Européia") if year == "2008" else prep_line


if __name__ == "__main__":
    args = sys.argv
    generate_csv(args[0], args[1], args[2])
