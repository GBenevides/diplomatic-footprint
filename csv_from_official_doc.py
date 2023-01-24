from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage
from io import StringIO
import csv
import re
from app_statics import *
import sys
import PyPDF2


def mk_degenerate_cases(year):
    cases = []
    if year == "2007":
        jamaica = blank_visit_entry(year)
        jamaica["Country"] = "Jamaica"
        jamaica["City/region"] = "Kingston"
        jamaica["Overview"] = jamaica_visit_2007_overview
        jamaica["Period"] = "9 de Agosto"
        jamaica["Host"] = "Host"
        cases.append(jamaica)
    return cases


def generate_csv(path, year, csv_prefix, verbose=False, pdfMiner=True, rearrange=True):
    pdf_text = convert_pdf_to_txt_pdfminer(path) if pdfMiner else convert_pdf_to_txt_pypdf2(path)
    raw_visits = visits_from_text(pdf_text, year)
    if verbose:
        for entry in raw_visits: print(entry)
    visits = rearrange_state_visits(raw_visits) if rearrange else raw_visits
    degenerate_cases = mk_degenerate_cases(year)
    visits = visits + degenerate_cases
    nb_visits = len(visits)
    if verbose:
        print("Number of visits", nb_visits)

    with open('data/' + csv_prefix + "-" + year + '.csv', mode='w') as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=data_visit_columns)
        writer.writeheader()
        for visit in visits:
            if verbose: print("Writing to csv: ", visit["City/region"], ",", visit["Country"])
            writer.writerow(visit)
    return nb_visits


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
                  '(Tanzânia), Lusaca (Zâmbia), Johannesburgo (África do Sul)']


def same_visit(visit, father_visit):
    months = ["janeiro", "fevereiro", "março", "abril", "maio", "junho", "julho", "agosto", "setembro", "outubro",
              "novembro", "dezembro"]
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
    append_visits(father_visit, rearranged)
    for v in rearranged:
        v["Overview"] = "\n".join(v["Overview"])
        v["Overview"] = v["Overview"].replace("–", "-") # More cleaning...
    return rearranged


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
        clone = father_visit.copy()
        clone["Country"] = c
        sub_visits.append(clone)
    return sub_visits


def blank_visit_entry(year):
    return {"year": year, "Overview": [], "Host": "Host", "Period": "", "Country": ""}


def format_location(loc):
    prepositions = ["De", "Do", "E", "Da", "Das", "Del"]
    loc = loc.strip().strip("()")
    loc = loc.title()
    for prep in prepositions:
        prep_spaces = f" {prep} "
        prep_spaces_lower = f" {prep.lower()} "
        loc = loc.replace(prep_spaces, prep_spaces_lower)
    return loc


def check_no_prohibitive_locs(line):
    prohibitive_terms = ["Celac", "Aprobras", "Sica", "Unasul", "Cedeao"]
    prohibitive_lines = ["Ouagadougou / Burkina Faso", "Brazzaville / Congo"]
    for term in prohibitive_terms:
        if term in line: return False
    for term in prohibitive_lines:
        if line == term: return False
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
        'Porto Príncipe (Haiti) e São Salvador (El Salvador)': ['Portsalv (HaitSalv)', "2008"],
        'Montevidéu (Uruguai) e Santiago (Chile)': ["Montiago (Uruchil)", "2010"],
        'Jerusalém (Israel), Belém (Palestina), Ramalá (Cisjordânia) e Amã (Jordânia)': ["Jerberama (Ispalcisjor)",
                                                                                         "2010"],
        'Buenos Aires (Argentina) e Montevidéu (Uruguai)': ["Buenvideu (Arguay)", "2010"],
        'Ilha do Sal (Cabo Verde), Malabo (Guiné Equatorial), Nairóbi (Quênia), Dar es Salaam': [
            'Ilhamanadarlujo (Caboguique Tanzamafr)', "2010"],
        'Rivera (Uruguai) e Assunção (Paraguai)': ["Rivasu (Urupara)", "2010"],
        'Caracas (Venezuela) e Bogotá (Colômbia)': ["Carabogo (Venelombia)", "2010"]
    }
    if raw in replace_lines.keys() and replace_lines[raw][1] == year:
        replacement = replace_lines[raw][0]
    return replacement


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
    last_is_overview = False
    current_visit = blank_visit_entry(year)

    # Iterate over the lines in the pdf text
    for line in pdf_text.split("\n"):
        line = line.strip()
        # Check if the line matches a header or month, it should be ignored
        if line in unwanted_lines:
            continue
        # Check if the line matches a period
        period_match = period_re.search(line)
        month_match = month_re.search(line)
        if period_match and (month_match or line in malformed_periods.keys()):
            current_visit["Period"] = malformed_periods[line] \
                if line in malformed_periods.keys() else period_match.group(1)
            continue
        if month_match and not overview_re.search(line):
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
                    and check_no_prohibitive_locs(replaced_line) and loc_country not in current_visit["Country"]:
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
        if overview_match:
            # if not current_visit["Overview"].endswith("\n"): current_visit["Overview"] += "\n"
            #            current_visit["Overview"] += "\n" + overview_match.group(1)
            line = " - " + line.lstrip("-").strip()
            current_visit["Overview"].append(line)
            last_is_overview = True
            continue
        # Sometimes the line will be the continuation of the line before
        if last_is_overview and line and line not in unwanted_lines and updated_re.search(line) and len(
                line) > 1 and not month__colon_re.search(line):
            # if not current_visit["Overview"].endswith("\n"): current_visit["Overview"] += "\n"
            prefix = " "
            if line.startswith("-"):  # or line[0].isupper():
                line = line.lstrip("-")
                prefix = ' - '
                current_visit["Overview"].append(prefix + line)
            else:
                current_visit["Overview"][-1] += prefix + line
            continue

    # We do not forget to append the last visit !
    state_visits.append(current_visit)
    return state_visits


if __name__ == "__main__":
    args = sys.argv
    generate_csv(args[0], args[1], args[2])
