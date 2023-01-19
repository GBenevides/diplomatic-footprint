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


def generate_csv(path, year, csv_prefix, verbose=False, pdfMiner=True, rearrange=True):
    pdf_text = convert_pdf_to_txt_pdfminer(path) if pdfMiner else convert_pdf_to_txt_pypdf2(path)
    raw_visits = visits_from_text(pdf_text, year)
    visits = rearrange_state_visits(raw_visits) if rearrange else raw_visits

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


headers = ["Presidência da República", "Casa Civil", "Secretaria Especial de Comunicação Social",
           "Viagens Internacionais", "Viagens Internacionais do Presidente da República",
           "Secretaria de Comunicação Social", "Secretaria de Imprensa"]


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
    same_country = father_visit["Country"] == visit["Country"]
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


def rearrange_state_visits(visits):
    rearranged = []
    father_visit = visits[0]
    for visit in visits[1:]:
        if visit["Period"] and not same_visit(visit, father_visit):
            if father_visit != {}:
                rearranged.append(father_visit)
            father_visit = visit
        else:
            father_visit["Overview"] += "\n\n-  [" + visit["City/region"] + "]"
            father_visit["Overview"] += visit["Overview"] + "\n"
    rearranged.append(father_visit)
    return rearranged


def blank_visit_entry(year):
    return {"year": year, "Overview": "", "Host": "Host", "Period": ""}


def visits_from_text(pdf_text, year):
    # Regular expressions to match the different parts in the official pdf
    month_re = re.compile(
        r"(Janeiro|Fevereiro|Março|Abril|Maio|Junho|Julho|Agosto|Setembro|Outubro|Novembro|Dezembro)\s*$",
        re.IGNORECASE)
    # location_re = re.compile(r"^([\w\s]+)\s+\(([\w\s]+)\)") # Parenthesis: Lima (Peru)
    # location_re = re.compile(r"^([\w\s]+)\s+\(([\w\s]+[a-z]+[\w\s]+)\)") # Same, but at least 1 lower case in country
    location_re = re.compile(r"^([\w\s]+)\s+\(([\w\s]+[a-z]+[\w\s]+|EUA)\)")  # Same, but accept EUA
    location2_re = re.compile(r"^(?!-)\s*([\w\s]+)/([\w\s]+)")  # Slash: Lima/Peru
    vowel_check = re.compile(r"[aeiouAEIOU]")
    period_re = re.compile(r"Período:\s+(.+)")
    period_re = re.compile(r"Período:?\s+(.+)")  # ":" optional

    overview_re = re.compile(r"(-\s.+)")
    updated_re = re.compile(r"^(?!Atualizado).*(?<!\d{2}/\d{2}/\d{4}$)")

    state_visits = []
    current_visit = blank_visit_entry(year)
    last_is_overview = False
    awkward_locs = ['Pequim, Sanya, Boao e Xian (China)']

    # Iterate over the lines in the pdf text
    for line in pdf_text.split("\n"):
        line = line.strip()
        # Check if the line matches a header or month, it should be ignored
        if line in headers:
            continue
        # Check if the line matches a period
        period_match = period_re.search(line)
        month_match = month_re.search(line)
        if period_match and month_match:
            current_visit["Period"] = period_match.group(1)
            continue
        if month_match and not overview_re.search(line):
            # print("month match", line)
            # current_month = month_match.group(1)
            continue
        # Check if the line matches a location AND has at least one vowel
        location_match = location_re.search(line)
        location_match2 = location2_re.search(line)
        awkward_match = re.search(r"([\w\s,]*)(\(.*\))", line) if line in awkward_locs else None
        if location_match or location_match2 or awkward_match:
            loc = location_match2 if location_match2 else location_match if location_match else awkward_match
            loc_country = loc.group(2).strip().strip("()")
            loc_region = loc.group(1).strip().strip("()")
            if re.search(vowel_check, loc_country) and (
                    len(loc_region.split()) < 5 or awkward_match) and "Celac" not in line:
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
                        raise KeyError("Missing key in line:", line, "Year", year)
                current_visit["City/region"] = f"{city}"
                current_visit["Country"] = f"{country}"
                continue
        # Check if the line matches an overview , that is, starts with "-"
        overview_match = overview_re.search(line)
        if overview_match:
            # if not current_visit["Overview"].endswith("\n"): current_visit["Overview"] += "\n"
            #            current_visit["Overview"] += "\n" + overview_match.group(1)
            current_visit["Overview"] += "\n" + line
            last_is_overview = True
            continue
        # Sometimes the line will be the continuation of the line before
        if last_is_overview and line and line not in headers and updated_re.search(line) and len(line) > 1:
            # if not current_visit["Overview"].endswith("\n"): current_visit["Overview"] += "\n"
            prefix = " "
            if line.startswith("-") or line[0].isupper():
                line = line.lstrip("-")
                prefix = '\n - '
            current_visit["Overview"] += prefix + line
            continue

    # We do not forget to append the last visit !
    state_visits.append(current_visit)
    return state_visits


if __name__ == "__main__":
    args = sys.argv
    generate_csv(args[0], args[1], args[2])
