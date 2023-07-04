expected_output_2009 = '''--------------\nLula 2009\nInconsistent posts:\n []\nTotal meetings: 108\nDone!'''
distinct_names_2004 = '''JC1
KO2
RI2
GBP
HC1
NE1
JZ1
OS1
CA3
AT1
AB6
SE3
LE3
HJ1
JA6
WJ1
BE3
BE4
RO1
VI1
GE1
NI1
AL6
JO13
JA7
JU7
OM1
PE3
AG3
JO14
AB7
BO3
MA16
JO15
AR3
LU3
GO1
JE4
AL4'''

distinct_names_mock = '''AB6
AT1
HC1
NE1
SE3'''

mock_data= [
    {
        "year": "2004",
        "Overview": " -str",
        "Host": [],
        "Period": "12 e 13 de Janeiro",
        "Country": "Mexico",
        "City/region": "Monterrey"
    },
    {
        "year": "2004",
        "Overview": " -sqddqd",
        "Host": [
            [
                "AT1"
            ],
            [
                "AB6"
            ]
        ],
        "Period": "25 a 28 de Janeiro",
        "Country": "India",
        "City/region": "New Deli, Agra and Bombay"
    },{
        "year": "2004",
        "Overview": " -sqddqd",
        "Host": [
            [
                "AT1"
            ],
            [
                "AB6"
            ]
        ],
        "Period": "25 a 28 de Janeiro",
        "Country": "India",
        "City/region": "New Deli, Agra and Bombay"
    },
    {
        "year": "2004",
        "Overview": " - Reuni\u00e3o tripartite com o presidente da Venezuela, Hugo Ch\u00e1vez Frias, e com o presidente da Argentina, Nestor Kirchner\n - Cerim\u00f4nia de Abertura da XII C\u00fapula do G-!\n - Primeira Sess\u00e3o Plen\u00e1ria dos Chefes de Estado e de Governo dos pa\u00edses membros do G-1\n - Encontro com o presidente do Ir\u00e3, Seyed Mohammed Khatami",
        "Host": [
            [
                "HC1",
                "NE1",
                "AT1"
            ],
            [
                "SE3",
                "SE3",
                "AB6",
                "AB6"
            ]
        ],
        "Period": "26 e 27 de Fevereiro",
        "Country": "Venezuela",
        "City/region": "Caracas"
    }]