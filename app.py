import streamlit as st
import pandas as pd
from streamlit_folium import st_folium
import folium
import json
import codecs
import logging
import os

logging.info('Viz Log Start')

TITLE = 'Diplomatic Footprint'
SUB_TITLE = "Visualizing Brazilian presidential trips and bilateral meetings over time"
abstract = "This project aims to observe the frequency and nature of high-level foreign visits and meetings made " \
           "by Brazilian heads of state in the 21st century, using official data from the ex-president gallery freely " \
           "available " \
           "online. The objective is to observe the foreign policy priorities, objectives, and biases of each " \
           "president, and to compare them across political backgrounds. The next steps involve expanding, " \
           "translating and " \
           "enriching the source data, which currently presents structural inconsistencies, as well as extracting " \
           "valuable " \
           "information from it. Also, different sources of data, such as political/economical freedom indicators," \
           "will be included."
MAP_WIDTH = "80%"
MAP_HEIGHT = 400

TEMER_KEY = "Michel Temer"
DILMA_KEY = "Dilma Roussef"
LULA_KEY = "Lula da Silva"

presidents_info = {
    LULA_KEY: {"short": "Lula", "duration": "2007-2010", "party": "Workers' Party (PT)",
               "political position": [["Progressivism", "https://en.wikipedia.org/wiki/Progressivism"],
                                      ["Democratic socialism", "https://en.wikipedia.org/wiki/Democratic_socialism"],
                                      ["Centre-left", "https://en.wikipedia.org/wiki/Centre-left_politics#_Brazil"],
                                      ]},
    DILMA_KEY: {"short": "Dilma", "duration": "2011-2016", "party": "Workers' Party (PT)",
                "political position": [["Progressivism", "https://en.wikipedia.org/wiki/Progressivism"],
                                       ["Democratic socialism", "https://en.wikipedia.org/wiki/Democratic_socialism"],
                                       ["Centre-left", "https://en.wikipedia.org/wiki/Centre-left_politics#_Brazil"],
                                       ]},
    TEMER_KEY: {"short": "Michel", "duration": "2016-2018", "party": "Brazilian Democratic Movement (MDB)",
                "political position": [["Big tent", "https://en.wikipedia.org/wiki/Big_tent#Brazil"],
                                       ["Economic liberalism", "https://en.wikipedia.org/wiki/Economic_liberalism"],
                                       ["Centre/centre-right", "https://en.wikipedia.org/wiki/Centre-right_politics"]]},
}


def create_map(data, pres, geo_data):
    if pres:
        df_filtered = data[data['president'] == pres]
    else:
        raise Exception(f'Could not filter data, unknown president {pres}')
    df_grouped = df_filtered.groupby('Country').size().reset_index(name='visits')
    m = folium.Map(location=[20, 0], no_single_click=True, no_double_click_zoom=True, max_bounds=True, min_zoom=2,
                   max_zoom=10, zoom_start=0, tiles='CartoDB Positron', continuous_world=False, no_touch=True,
                   dragging=True, zoom_control=False, scroll_wheel_zoom=True, width=MAP_WIDTH, height=500)

    # Add a choropleth layer to the map
    layer = folium.Choropleth(
        geo_data=geo_data,
        name='visits',
        data=df_grouped,
        columns=['Country', 'visits'],
        key_on='feature.properties.name',
        fill_color='YlGn',
        fill_opacity=1.0,
        line_opacity=1.0,
        legend_name='Number of visits',
        highlight=True,
        #bins=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    ).add_to(m)

    colormap = layer.color_scale
    colormap.caption = 'Number of Visits'
    colormap.max_labels = 10
    colormap.width = 500

    layer.geojson.add_child(folium.features.GeoJsonTooltip(['name', 'name_pt'], labels=False))

    st_map = st_folium(m, width=MAP_WIDTH, height=MAP_HEIGHT, returned_objects=["last_active_drawing"], key="testKey")

    active_country = ''
    if st_map['last_active_drawing']:
        active_country = st_map['last_active_drawing']['properties']['name']
    return active_country, df_filtered


def stats_from_pres(df_visits, term):
    df_president = df_visits[df_visits["president"] == term]
    num_distinct_countries = df_president["Country"].nunique()
    president_groupby_year = df_president.groupby(["year"])
    visits_per_year = president_groupby_year.size()
    most_visits_year = visits_per_year.idxmax()
    most_visits = visits_per_year.max()
    return "{:.2f}".format(president_groupby_year.size().mean()), str(most_visits_year) + " [" + str(most_visits) + "]", str(
        num_distinct_countries)


def display_presidential_sidebar(df_visits):
    st.sidebar.markdown("### Presidential Term")
    term_selected = st.sidebar.selectbox(
        'Select a Presidential term and click on a country to visualize the details of each state visit.',
        presidents_info, 0)
    logging.info(f'President filter: {term_selected} ')
    st.sidebar.markdown("---")
    st.sidebar.markdown("### Party : {party}".format(party=presidents_info[term_selected]["party"]))
    for position in presidents_info[term_selected]["political position"]:
        st.sidebar.markdown("- [{text}]({url})".format(text=position[0], url=position[1]))
    st.sidebar.markdown("---")
    visits_per_year, most_visits_year, distinct_countries = stats_from_pres(df_visits, term_selected)
    st.sidebar.subheader("Overview of International Trips")
    st.sidebar.metric(label="Average Visits per Year", value=visits_per_year)
    st.sidebar.metric(label="Busiest Year [Countries Visited]", value=most_visits_year)
    st.sidebar.metric(label="Total Countries Visited", value=distinct_countries)
    st.sidebar.markdown("---")
    st.sidebar.markdown("Author: [{text}]({url})".format(text="Gabriel Benevides", url="https://www.linkedin.com/in/gabriel-benevides/"))
    return term_selected


def on_country_click(country, df):
    if not country:
        st.write("Click on a country to display a state visit overview.")
    else:
        df_country = df.loc[df['Country'] == country]
        if df_country.empty:
            st.subheader(f'No official state visits to {country} on record.')
        else:
            st.subheader(f'{country} Visits')
            for index, row in df_country.iterrows():
                period = str(row['Period'])
                region = str(row["City/region"])
                year = str(row['year'])
                expander = st.expander(year + ": " + region + " - " + period)
                overview_of_trip = row['Overview'].lstrip('\n\r').replace("", '"').replace("", '"')
                for line in overview_of_trip.splitlines():  # Normalize newline breaks !
                    expander.write(line)
                # expander.write(clean_overview_of_trip)


def main():
    st.set_page_config(TITLE, page_icon=":guardsman:", layout="wide", initial_sidebar_state="expanded")
    st.title(TITLE)
    st.caption(SUB_TITLE)
    # st.markdown("###### {abstract}".format(abstract=abstract))
    st.write('<style>div.block-container{padding-top:1.5rem;}</style>', unsafe_allow_html=True)
    st.markdown(
        f'''
                <style>
                    section[data-testid="stSidebar"] > div > div:nth-child(2) {{
                        padding-top: {1}rem;
                    }}
                </style>
                ''', unsafe_allow_html=True)

    # Load Data - Lula
    df_visits_lula_2006 = pd.read_csv('data/Lula_official_visits-2006.csv', encoding='unicode_escape')
    df_visits_lula_2007 = pd.read_csv('data/Lula_official_visits-2007.csv', encoding='unicode_escape')
    df_visits_lula_2008 = pd.read_csv('data/Lula_official_visits-2008.csv', encoding='unicode_escape')
    df_visits_lula_2009 = pd.read_csv('data/Lula_official_visits-2009.csv', encoding='unicode_escape')
    df_visits_lula_2010 = pd.read_csv('data/Lula_official_visits-2010.csv', encoding='unicode_escape')
    df_visits_lula = pd.concat([df_visits_lula_2006, df_visits_lula_2007, df_visits_lula_2008, df_visits_lula_2009, df_visits_lula_2010])
    df_visits_lula["president"] = LULA_KEY

    # Load Data - Dilma
    df_dilma11 = pd.read_csv('data/Dilma_official_visits-2011.csv', encoding='unicode_escape')
    df_dilma12 = pd.read_csv('data/Dilma_official_visits-2012.csv', encoding='unicode_escape')
    df_dilma13 = pd.read_csv('data/Dilma_official_visits-2013.csv', encoding='unicode_escape')
    df_dilma14 = pd.read_csv('data/Dilma_official_visits-2014.csv', encoding='unicode_escape')
    df_dilma15 = pd.read_csv('data/Dilma_official_visits-2015.csv', encoding='unicode_escape')
    df_dilma16 = pd.read_csv('data/Dilma_official_visits-2016.csv', encoding='unicode_escape')
    df_dilma = pd.concat([df_dilma11, df_dilma12, df_dilma13, df_dilma14, df_dilma15, df_dilma16])
    df_dilma["president"] = DILMA_KEY

    # Load Data - Temer
    df_visits_temer_2017 = pd.read_csv('data/Temer_official_visits-2017.csv', encoding='unicode_escape')
    df_visits_temer_2018 = pd.read_csv('data/Temer_official_visits-2018.csv', encoding='unicode_escape')
    df_visits_temer = pd.concat([df_visits_temer_2017, df_visits_temer_2018])
    df_visits_temer["president"] = TEMER_KEY

    # Join Data
    df_visits = pd.concat([df_visits_lula, df_dilma, df_visits_temer])

    # Display sidebar
    pres = display_presidential_sidebar(df_visits)
    # exp = st.expander(expanded=False, label="Project Overview")
    st.markdown("###### {abstract}".format(abstract=abstract))
    st.header(f'{pres} ({presidents_info[pres]["duration"]})')

    # Load geo data and create map
    f = codecs.open('./data/customGeo.json', 'r', 'utf-8')
    geo_data = json.loads(f.read())
    active_country, df_filtered = create_map(df_visits, pres, geo_data)
    logging.info(f'{active_country} Visits')

    # Line separation
    st.markdown("""---""")

    # Stats section
    on_country_click(active_country, df_filtered)


if __name__ == "__main__":
    dir_path = os.path.dirname(os.path.realpath(__file__))
    #logging.info('Cwd: ' + dir_path)
    #logging.info('List dir: ')
    #for s in os.listdir(): logging.info(s)
    main()
