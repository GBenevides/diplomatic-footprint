from csv_from_official_doc import generate_csv

data_path_prefix = "data/Viagens-internacionais-"
verbose = False
temer = {"2017": 9, "2018": 8}
dilma = {"2011": [17], "2012": 15, "2013": 18, "2014": 12, "2015": 16, "2016": 3}
lula = {}


def generate_csv_by_year(name, years_visits):
    for year, visits in years_visits.items():
        print(name, year)
        path = f'{data_path_prefix}{name}-{year}.pdf'
        use_pdf_miner = True
        if type(visits) is list:
            use_pdf_miner = False
            visits = visits[0]

        nb_visits = generate_csv(path, year, csv_prefix=name + "_official_visits", verbose=verbose,
                                 pdfMiner=use_pdf_miner)
        if nb_visits == visits:
            print("Done!")
            print("--------------")
        else:
            raise Exception(
                "Inconsistent number of visits! Expected " + str(visits) + " and found " + str(nb_visits) + ".")


print("Generating files")
print("--------------")
generate_csv_by_year("Dilma", dilma)
generate_csv_by_year("Temer", temer)
