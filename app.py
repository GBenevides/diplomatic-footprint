import streamlit as st
import pandas as pd
from streamlit_folium import st_folium
import folium
import json
import app_statics
import codecs
import logging
import os
from collections import Counter

logging.debug('Viz Log Start')

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
    LULA_KEY: {"short": "Lula", "duration": "2004-2010", "party": "Workers' Party (PT)",
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
        # bins=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
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


def trip_stats_from_pres(df_visits, term):
    df_president = df_visits[df_visits["president"] == term]
    num_distinct_countries = df_president["Country"].nunique()
    president_groupby_year = df_president.groupby(["year"])
    visits_per_year = president_groupby_year.size()
    most_visits_year = visits_per_year.idxmax()
    most_visits = visits_per_year.max()
    return "{:.1f}".format(president_groupby_year.size().mean()), str(most_visits_year) + " [" + str(
        most_visits) + "]", str(
        num_distinct_countries)


def display_presidential_sidebar(df_visits):
    st.sidebar.markdown("### Presidential Term")
    term_selected = st.sidebar.selectbox(
        'Select a Presidential term and click on a country to visualize the details of each state visit.',
        presidents_info, 0)
    logging.info(f'President filter: {term_selected} ')
    # st.sidebar.markdown("---")
    # st.sidebar.markdown("### Party : {party}".format(party=presidents_info[term_selected]["party"]))
    # for position in presidents_info[term_selected]["political position"]:
    #    st.sidebar.markdown("- [{text}]({url})".format(text=position[0], url=position[1]))
    st.sidebar.markdown("---")
    visits_per_year, most_visits_year, distinct_countries = trip_stats_from_pres(df_visits, term_selected)
    st.sidebar.subheader("Overview of International Trips")
    st.sidebar.metric(label="Average Visits per Year", value=visits_per_year)
    st.sidebar.metric(label="Busiest Year [Countries Visited]", value=most_visits_year)
    st.sidebar.metric(label="Total Countries Visited", value=distinct_countries)
    st.sidebar.markdown("---")
    combined_counts, avg_meetings_year = meeting_stats_from_pres(df_visits, term_selected)
    st.sidebar.subheader("Overview of Bilateral Meetings and Encounters")
    st.sidebar.metric(label="Average Meetings per Year", value=round(avg_meetings_year, 1))
    st.sidebar.metric(label="Average Meetings per Visit", value=0)
    st.sidebar.markdown("Most Frequent Encounters")

    # Top meetings table with filter
    # Post filter
    pre_filter_list = [p for p in app_statics.posts_mapping.values() if p not in app_statics.dirty_posts]
    seen = set()
    filtered_list = [e for e in pre_filter_list if not (e in seen or seen.add(e))]
    display_threshold = False
    threshold = None
    st.sidebar.markdown("Filter by post:")
    selections_post = []
    show_on_left_side = True
    post_col1, post_col2 = st.sidebar.columns(2)
    for possible_post in filtered_list:
        if show_on_left_side:
            include_post = post_col1.checkbox(possible_post, value=True)
        else:
            include_post = post_col2.checkbox(possible_post, value=True)
        if include_post:
            selections_post.append(possible_post)
        show_on_left_side = not show_on_left_side

    # Country filter
    pre_filter_list_country = [p for p in app_statics.country_mapping.values() if
                               p not in app_statics.dirty_countries and ";" not in p]
    seen_country = set()
    distinct_list_country = [e for e in pre_filter_list_country if not (e in seen or seen.add(e))]
    # No filter : all countries
    selections_country = st.sidebar.multiselect("Filter by post/country/institution :", distinct_list_country, [])
    if not selections_country or len(selections_country) == 0:
        selections_country = distinct_list_country
    combined_counts = {entry: count for entry, count in combined_counts.items() if
                       any(s in app_statics.leaders_mapping[entry]['posts'] for s in selections_post)
                       and any(s in app_statics.leaders_mapping[entry]['country'] for s in selections_country)}
    if display_threshold:
        threshold = st.sidebar.slider('Cut entries', 1, 300, 3)
    top_entries = Counter(combined_counts).most_common(threshold)

    transform_for_table = {app_statics.leaders_mapping[key]['figure']: [app_statics.leaders_mapping[key]['country'],
                                                                        app_statics.leaders_mapping[key]['posts'], value] for key, value in top_entries}
    table_data = []
    for leader, data in transform_for_table.items():
        table_data.append([leader, data[0], data[1], data[2]])
    df = pd.DataFrame(table_data, columns=["Name", "Country / Institution", "Post(s)", "#"])
    st.sidebar.dataframe(df, hide_index=True, use_container_width=False)

    st.sidebar.markdown("---")
    st.sidebar.markdown("Author: [{text}]({url})".format(text="Gabriel Benevides",
                                                         url="https://www.linkedin.com/in/gabriel-benevides/"))
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
                # overview_col, meetings_col = expander.columns([2, 1])
                agenda_tab, meetings_summary_tab = expander.tabs(['Agenda', 'Meetings Summary'])

                overview_of_trip = row['Overview'].lstrip('\n\r').replace("", '"').replace("", '"')
                meetings_in_visit_set = {}
                for line in overview_of_trip.splitlines():  # Normalize newline breaks !
                    agenda_tab.write(line)
                    for instance in row["Host"]:
                        for key in instance:
                            leader = app_statics.leaders_mapping[key]
                            meetings_in_visit_set[leader['figure']] = [leader['country'], leader["posts"]]
                if len(meetings_in_visit_set) > 0:
                    df = pd.DataFrame([[key, value[1], value[0]] for key, value in meetings_in_visit_set.items()],
                                      columns=["Name", "Post", "Country / Institution"])
                    print("data:", df)
                    meetings_summary_tab.dataframe(df, hide_index=True, use_container_width=False)
                else:
                    meetings_summary_tab.write("No bilateral meetings / private encounters.")
                # TODO Unit test Russia


def load_data(data_path, start_year, end_year, name_prefix):
    years_data = []
    data_extension = '.json'  # json / csv
    encoding = "utf-8"  # utf-8 / unicode_escape
    for i in range(start_year, end_year):
        path = data_path + "/" + name_prefix + '_official_visits-' + str(i) + data_extension
        years_data.append(pd.read_json(path, encoding=encoding))
    return pd.concat(years_data)


def meeting_stats_from_pres(df, term, distinct_hosts_by_entry=True):
    df_president = df[df["president"] == term]
    ranges = {
        LULA_KEY: range(2004, 2011),
        DILMA_KEY: range(2011, 2017),
        TEMER_KEY: range(2017, 2019)
    }
    total_meetings = 0
    combined_counts = Counter()
    for year in ranges[term]:
        df_year = df_president[df_president["year"] == year]
        meetings_in_trip, sorted_host_code_counts, codes_with_max_count = meetings_stats_by_year(df_year,
                                                                                                 distinct_hosts_by_entry)
        total_meetings += meetings_in_trip
        combined_counts += Counter(sorted_host_code_counts)
    avg_meetings_year = total_meetings / len(ranges[term])
    return combined_counts, avg_meetings_year


def meetings_stats_by_year(df, distinct_hosts_by_entry=True):
    # Distinct hosts and Individual hosts
    # We want distinct hosts by visit
    # Iterate over each row in the DataFrame
    host_code_counts = {}
    meetings_in_trip = 0
    for c, row in df.iterrows():
        hosts = row['Host']
        hosts_by_entry = sum(hosts, [])
        if distinct_hosts_by_entry:
            hosts_by_entry = set(hosts_by_entry)  # Flatten the host list and remove duplicates
        # Increment the count for each host code
        meetings_in_trip += len(hosts_by_entry)
        for host_code in hosts_by_entry:
            host_code_counts[host_code] = host_code_counts.get(host_code, 0) + 1
    sorted_host_code_counts = dict(sorted(host_code_counts.items(), key=lambda x: x[1], reverse=True))
    max_count = max(sorted_host_code_counts.values())
    codes_with_max_count = [code for code, count in sorted_host_code_counts.items() if count == max_count]

    return meetings_in_trip, sorted_host_code_counts, codes_with_max_count


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

    # Load Data
    data_path = 'data'
    # Lula
    df_visits_lula = load_data(data_path, 2004, 2011, "Lula")
    df_visits_lula["president"] = LULA_KEY

    # Dilma
    df_dilma = load_data(data_path, 2011, 2017, "Dilma")
    df_dilma["president"] = DILMA_KEY

    # Temer
    df_visits_temer = load_data(data_path, 2017, 2019, "Temer")
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
    logging.info('Cwd: ' + dir_path)
    # logging.info('List dir: ')
    # for s in os.listdir(): logging.info(s)
    main()
