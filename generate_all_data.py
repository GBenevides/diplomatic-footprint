from data_from_official_doc import generate_csv

dilma = {"2011": [17, 44], "2012": [15, 35], "2013": [18, 23], "2014": [12, 19], "2015": [16, 38], "2016": [3, 3]}
temer = {"2017": [9, 25], "2018": [8, 20]}
lula = {"2004": [21, 49], "2005": [29, 54], "2006": [16, 36], "2007": [36, 81], "2008": [33, 89], "2009": [40, 108],
        "2010": [35, 56]}

verbose = False


def generate_data_by_year(name, years_visits, data_path_prefix, testMode=False):
    for year, [expected_visits, expected_meetings] in years_visits.items():
        print("--------------")
        print(name, year)
        path = f'{data_path_prefix}{name}-{year}.pdf'
        use_pdf_miner = True

        nb_visits, nb_meetings = generate_csv(path, year, data_path_prefix=name + "_official_visits", verbose=verbose,
                                              pdfMiner=use_pdf_miner, testMode=testMode)
        if nb_visits == expected_visits and nb_meetings == expected_meetings:
            print("Done!")
        else:
            raise Exception("Expected", str(expected_visits), "visits and", str(expected_meetings), "meetings, but "
                                                                                                    "actually found "
                            , str(nb_visits), "visits and", str(nb_meetings), "meetings.")
    return 0


if __name__ == "__main__":
    print("Generating files:")
    std_data_path_prefix = "data/Viagens-internacionais-"
    generate_data_by_year("Lula", lula, std_data_path_prefix)
    generate_data_by_year("Dilma", dilma, std_data_path_prefix)
    generate_data_by_year("Temer", temer, std_data_path_prefix)
