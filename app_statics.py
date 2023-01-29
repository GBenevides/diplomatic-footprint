columns_eng = {
    "País": "Country",
    "Cidade/Região": "City/region",
    "Período": "Period",
    "Anfitrião": "Host",
    "Notas": "Overview",

}
year_col = "year"
data_visit_columns = list(columns_eng.values())
data_visit_columns.append(year_col)

country_mapping = {
    "Argélia": "Algeria",
    "Angola": "Angola",
    "Alemanha": "Germany",
    "Andorra": "Andorra",
    "Argentina": "Argentina",
    "Armenia": "Armenia",
    "Austria": "Austria",
    "Áustria": "Austria",
    "Austrália": "Australia",
    "Azerbaijão": "Azerbaijan",
    "Bélgica": "Belgium",
    "Bolívia": "Bolivia",
    "Bósnia e Herzegovina": "Bosnia and Herzegovina",
    "Brasil": "Brazil",
    "Bulgária": "Bulgaria",
    "Bolivia": "Bolivia",
    "Canadá": "Canada",
    "Chile": "Chile",
    "China": "China",
    "Catar": "Qatar",
    "Colômbia": "Colombia",
    "Costa Rica": "Costa Rica",
    "Croácia": "Croatia",
    "Cuba": "Cuba",
    "Dinamarca": "Denmark",
    "Equador": "Ecuador",
    "Eslováquia": "Slovakia",
    "Eslovênia": "Slovenia",
    "Espanha": "Spain",
    "Estados Unidos": "United States of America",
    "EUA": "United States of America",
    "Eua": "United States of America",
    "Estônia": "Estonia",
    "Etiópia": "Ethiopia",
    "Finlândia": "Finland",
    "França": "France",
    "Geórgia": "Georgia",
    "Grécia": "Greece",
    "Guatemala": "Guatemala",
    "Guiana": "Guyana",
    "Gana": "Ghana",
    "Honduras": "Honduras",
    "Hungria": "Hungary",
    "Holanda": "Holland",
    "Haiti": "Haiti",
    "Islândia": "Iceland",
    "Índia": "India",
    "Japão": "Japan",
    "Cabo Verde": "Cape Verde",
    "África do Sul": "South Africa",
    "Ã�frica do Sul": "South Africa",
    "Irlanda": "Ireland",
    "Itália": "Italy",
    "Inglaterra": "United Kingdom",
    "Latvia": "Latvia",
    "Liechtenstein": "Liechtenstein",
    "Lituânia": "Lithuania",
    "Luxemburgo": "Luxembourg",
    "Macedônia": "Macedonia",
    "Malta": "Malta",
    "México": "Mexico",
    "Moldova": "Moldova",
    "Mônaco": "Monaco",
    "Montenegro": "Montenegro",
    "Países Baixos": "Netherlands",
    "Nicarágua": "Nicaragua",
    "Noruega": "Norway",
    "Panamá": "Panama",
    "Paraguai": "Paraguay",
    "Peru": "Peru",
    "Polônia": "Poland",
    "Portugal": "Portugal",
    "Reino Unido": "United Kingdom",
    "República Checa": "Czech Republic",
    "República Tcheca": "Czech Republic",
    "Romênia": "Romania",
    "Rússia": "Russia",
    "San Marino": "San Marino",
    "Sérvia": "Serbia",
    "Sérvia e Montenegro": "Serbia and Montenegro",
    "Suécia": "Sweden",
    "Suíça": "Switzerland",
    "Suriname": "Suriname",
    "Turquia": "Turkey",
    "Ucrânia": "Ukraine",
    "Uruguai": "Uruguay",
    "Venezuela": "Venezuela",
    "Guiné Equatorial": "Eq. Guinea",
    "Nigéria": "Nigeria",
    "Moçambique": "Mozambique",
    "Botsuana": "Botswana",
    "Botsuana) e Johanesburgo (África do Sul": "Botswana;South Africa",
    "Jamaica": "Jamaica",
    "Burcongo": "Burkina Faso;Congo",
    "Chile) e Buenos Aires (Argentina": "Chile;Argentina",
    "Honduras) e  Manágua  (Nicarágua": "Honduras;Nicaragua",
    "El Salvador": "El Salvador",
    "Vietnã": "Vietnam",
    "Indonésia":"Indonesia",
    "Burkina Faso" : "Burkina Faso",
    "Timor-Leste" : "Timor-Leste",
    "Salvadorcuba" : "El Salvador;Cuba",
    "France Eng" : "France;United Kingdom",
    "Trinidad e Tobago" : "Trinidad and Tobago",
    "Arábia Saudita" : "Saudi Arabia",
    "Cazaquistão" : "Kazakhstan",
    "Líbia" : "Libya",
    "Salv Guate" : "El Salvador;Guatemala",
    "Palestina" : "Palestina",
    "Israel" : "Israel",
    "Cisjordânia" : "West Bank and Gaza",
    "Jordânia" : "Jordan",
    "Irã" : "Iran",
    "Tanzânia" : "Tanzania",
    "Quênia" :"Kenya",
    "Coreia do Sul" : "South Korea",
    'Coréia do Sul' : "South Korea",
    "Zâmbia":"Zambia",
    "Haitsalv" : "Haiti;El Salvador",
    "Uruchil" : "Uruguay;Chile",
    "Ispalcisjor" : "Israel;Palestine;West Bank and Gaza;Jordan",
    "Arguay":"Argentina;Uruguay",
    "Caboguique Tanzamafr": "Cape Verde;Eq. Guinea;Kenya;Tanzania;Zambia;South Africa",
    "Urupara" : "Uruguay;Paraguay",
    "Venelombia" : "Venezuela;Colombia",
    "Congo":"Congo",
    "Gabão":"Gabon",
    "República Dominicana":"Dominican Rep.",
    "Saotomeeprincipe":"São Tomé and Príncipe",
    "Camarões":"Cameroon",
    "Senegal":"Senegal",
    "Escócia":"United Kingdom",
    "República Portuguesa" : "Portugal",
    "Italia":"Italy",
    "Guiné Bissau": "Guinea-Bissau",
    "Comitê Olímpico Internacional" : "International Olympic Committee",
    "Nações Unidas" : "United Nations"
}

city_mapping = {
    "Carabogo": "Caracas and Bogota",
    "Bissau":"Bissau",
    "Ciudaguyana" : "Ciudad Guyana",
    "Salamanca": "Salamanca",
    "Puerto Maldonado":"Puerto Maldonado",
    "Cidade do Porto":"Porto",
    "Tóquio":"Tokyo",
    "Gleneagles":"Gleneagles",
    "Nagóia":"Nagoya",
    "Dacar":"Dakar",
    "Aquila": "Rome and L'Aquila",
    "Brazzaville":"Brazzaville",
    "Rivasu" : "Rivera and Assuncion",
    "Ilhamanadarlujo": "Sal, Malabo, Nairobi, Dar es Salaam, Lusaca, Pretoria and Johannesburg",
    "Buenvideu" : "Buenos Aires and Montevideo",
    "Jerberama" : "Jerusalem, Bethlehem, Ramallah and Amman",
    "Montiago" : "Montevideo and Santiago",
    "Rivera" : "Rivera",
    "Mar del Plata" : "Mar del Plata",
    "San Juan" : "San Juan",
    "Seul" : "Seoul",
    "Amã":"Amman",
    "Dar Es Salaam" : "Dar es Salaam",
    "Lusaca":"Lusaka",
    "Cancún" : "Cancún",
    "Jerusalém" : "Jerusalem",
    "Belém" : "Bethlehem",
    "Ramalá" : "Ramallah",
    "Argel": "Algers",
    "Sirte" : "Sirte",
    "Genebra" : "Geneva",
    "Chimoré" : "Chimoré",
    "Bariloche" : "Bariloche",
    "Nova Iorque e Pittsburgh":"New York and Pittsburgh",
    "Pittsburgh" : "Pittsburgh",
    "Ecaterimburgo" :"Yekaterinburg" ,
    "Berlim" : "Berlin",
    "Isla Margarita": "Isla Margarita",
    "Caracas e El Tigre" : "Caracas and El Tigre",
    "El Tigre":"El Tigre",
    "Lisboa e Estoril" : "Lisbon and Estoril",
    "Estoril": "Estoril",
    "Kiev" : "Kiev",
    "Trípoli": "Tripoli",
    "Istambul" : "Istanbul",
    "Astana" : "Astana",
    "San Salvador" : "San Salvador",
    "São José" : "San Jose",
    "Moscou": "Moscow",
    "Oslo": "Oslo",
    "Hamburgo": "Hamburg",
    "Mendoza": "Mendoza",
    "Lisboa": "Lisbon",
    "Pequim": "Beijing",
    "Xiamen": "Xiamen",
    "Córdoba": "Cordoba",
    "Nova York": "New York",
    "Buenos Aires": "Buenos Aires",
    "Zurique": "Zurich",
    "Vinã del Mar": "Viña del Mar",
    "Viña del Mar" : "Viña del Mar",
    "Parislondres" : "Paris and London",
    "Lima": "Lima",
    "Assunção": "Asuncion",
    'Ilha do Sal': "Sal",
    "Puerto Vallarta": "Puerto Vallarta",
    "Joanesburgo": "Johannesburg",
    "Johanesburgo": "Johannesburg",
    "Johannesburgo": "Johannesburg",
    "Quito": "Quito",
    "Santiago": "Santiago",
    "Nova Iorque": "New York",
    "La Paz": "La Paz",
    "San José": "San Jose",
    "Colônia": "Colonia del Sacramento",
    "Montevidéu": "Montevideo",
    "Cidade do Panamá": "Panama City",
    "Cidade do México": "Mexico City",
    "Bruxelas": "Brussels",
    "Washington": "Washington",
    "São Francisco": "San Francisco",
    "Ufa": "Ufa",
    "Roma e Milão": "Rome and Milan",
    "Roma": "Rome",
    "Milão": "Milan",
    "Bogotá": "Bogota",
    "Estocolmo": "Stockholm",
    "Linköping": "Linköping",
    "Helsinque": "Helsinki ",
    "Antália": "Antalya",
    "Paris": "Paris",
    "Malabo": "Malabo",
    "Abuja": "Abuja",
    "Caracas": "Caracas",
    "Durban": "Durban",
    "Adis Abeba": "Adis Abeba",
    "Paramaribo": "Paramaribo",
    "Petersburgo": "Saint Petersburg",
    "São Petersburgo": "Saint Petersburg",
    "Joanesbugo": "Johannesburg",
    "Davos": "Davos",
    "Província de Artemisa": "Artemisa Province",
    "Havana": "Havana",
    "Valparaiso": "Valparaiso",
    "Doha": "Doha",
    "Brisbane": "Brisbane",
    "Província de Entre Rios": "Entre Rios Province",
    "Porto Príncipe": "Port-au-Prince",
    "Hannover": "Hanover",
    "Nova Délhi": "New Delhi",
    "Nova Delhi": "New Delhi",
    "Boston": "Boston",
    "Cartagena das Índias": "Cartagena ",
    "Los Cabos": "Los Cabos",
    "Londres": "London",
    "Cadiz": "Cadiz",
    "Sevilha": "Seville",
    "Madri": "Madrid",
    "Lisboa e Coimbra": "Lisbon and Coimbra",
    "Sanya": "Sanya",
    "Boao": "Boao",
    "Xian": "Xian",
    "Sófia": "Sofia",
    "Gorna Oryahovitsa": "Gorna Oryahovitsa",
    "Ancara": "Ankara",
    "Pretória": "Pretoria",
    "Maputo": "Maputo",
    "Luanda": "Luanda",
    "Cannes": "Cannes",
    "Pequim, Sanya, Boao e Xian": "Pequim, Sanya, Boao e Xian",
    "Gaborone": "Gaborone and Johannesburg",
    "Puerto Iguazú": "Puerto Iguazú",
    "Viena": "Viena",
    "Ciudad Guayana": "Ciudad Guayana",
    "Cochabamba": "Cochabamba",
    "Valparaíso  e Viña del Mar": "Valparaíso and Viña Del Mar",
    "Georgetown": "Georgetown",
    "Barcelona e Isla Margarita": "Barcelona and Margarita Island",
    "Berlim e Heiligendamm": "Berlin and Heiligendamm",
    "Tegucigalpa": "Tegucigalpa and Managua",
    "Manágua": "Managua",
    "Kingston": "Kingston",
    "Copenhague": "Copenhagen",
    "Ouagabraza": "Ouagadougou and Brazzaville",
    "Ouagadougou":"Ouagadougou",
    "Cidade da Guatemala": "Guatemala City",
    "Haia e Amsterdã": "The Hague and Amsterdam",
    "Praga": "Prague",
    "Acra": "Accra",
    "Portsalv": "Port-au-Prince and San Salvador",
    "São Salvador" : "San Salvador",
    "San Miguel de Tucumán": "San Miguel de Tucumán",
    "Sapporo":"Sapporo",
    "Hanói":"Hanoi",
    "Jacarta":"Jakarta",
    "Riberalta" :"Riberalta",
    "Letícia": "Leticia",
    "Madri e Toledo" : "Madrid and Toledo",
    "Vaticano" : "Vatican",
    "Díli": "Dili",
    "Salv Cuba" : "San Salvador and Havana",
    "Punta Arenas" : "Punta Arenas",
    "Oiapoque":"Oyapock",
    "Arroyo Concepción":"Arroyo Concepción",
    "Maracaibo" : "Maracaibo",
    "Washington e Nova Iorque" : "Washington and New York",
    "Porto de Espanha" : "Port of Spain",
    "Riade" : "Riyadh",
    "Salvadorguate" : "San Salvador and Guatemala City",
    "Teerã" : "Tehran",
    "Nairóbi" : "Nairobi",
    "Monterrey":"Monterrey",
    "Pequim e Xangai":"Beijing and Shanghai",
    "Guadalajara" : "Guadalajara",
    "Libreville":"Libreville",
    "Cobija":"Cobija",
    "Santo Domingo":"Santo Domingo",
    "Cuzco":"Cuzco",
    "Dehliagramum":"New Deli, Agra and Bombay",
    "Santacsi": "Santa Cruz de la Sierra",
    "Saotome" : "São Tomé",
'Montevidéu  e Paysandú' : "Montevideo and Paysandú",
    "Iaundê": "Yaoundé"
}

jamaica_visit_2007_overview = "- Chegada do presidente Luiz Inácio Lula da Silva a Kingston / Jamaica\n" \
                              "- Visita de cortesia ao senhor Kenneth O. Hall, governador-geral da Jamaica\n" \
                              "- Cerimônia de inauguração da Usina de Etanol da Jamaica Broilers Group\n" \
                              "- Encerramento do Fórum de Negócios sobre Etanol, Biodiesel, Cimento, Gipsita, Soja e Alumínio\n" \
                              " - Encontro privado com a senhora Portia Simpson Miller, primeira-ministra da Jamaica\n- Cerimônia de Assinatura de Atos e Declaração à Imprensa\n" \
                              "- Almoço oferecido pela senhora Portia Simpson Miller, primeira-ministra da Jamaica\n" \
                              "- Audiência ao senhor Bruce Golding, líder da oposição no Parlamento\n" \
                              "- Partida do Presidente da República para a Cidade do Panamá / Panamá\n"

months = ["janeiro", "fevereiro", "março", "abril", "maio", "junho", "julho", "agosto", "setembro", "outubro",
              "novembro", "dezembro"]