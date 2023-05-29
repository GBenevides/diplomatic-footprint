from csv_from_official_doc import generate_csv

data_path_prefix = "data/Viagens-internacionais-"
temer = {"2017": 9, "2018": 8}
dilma = {"2011": 17, "2012": 15, "2013": 18, "2014": 12, "2015": 16, "2016": 3}
lula = {"2004": 21, "2005": 29, "2006": 16, "2007": 36, "2008": 33, "2009": 40, "2010": 35}
lula = {"2008": [33, 72], "2009": [40, 52]}
lula = {"2009": [40, 108]}
verbose = False


def generate_csv_by_year(name, years_visits):
    for year, [expected_visits, expected_meetings] in years_visits.items():
        print(name, year)
        path = f'{data_path_prefix}{name}-{year}.pdf'
        use_pdf_miner = True

        nb_visits, nb_meetings = generate_csv(path, year, csv_prefix=name + "_official_visits", verbose=verbose,
                                 pdfMiner=use_pdf_miner)
        if nb_visits == expected_visits and nb_meetings == expected_meetings:
            print("Done!")
            print("--------------")
        else:
            raise Exception("Expected" , str(expected_visits) , "visits and", str(expected_meetings), "meetings, but actually found"
                            , str(nb_visits), "visits and", str(nb_meetings), "meetings.")


print("Generating files")
print("--------------")
generate_csv_by_year("Lula", lula)
#generate_csv_by_year("Dilma", dilma)
#generate_csv_by_year("Temer", temer)
