countries_dict = {'Afghanistan': 'AF', 'Ägypten': 'EG', 'Åland Islands': 'AX', 'Albanien': 'AL', 'Algerien': 'DZ', 'Andorra': 'AD', 'Angola': 'AO', 'Anguilla': 'AI', 'Antarktis': 'AQ', 'Antigua und Barbuda': 'AG', 'Äquatorial Guinea': 'GQ', 'Argentinien': 'AR', 'Armenien': 'AM', 'Aruba': 'AW', 'Aserbaidschan': 'AZ', 'Äthiopien': 'ET', 'Australien': 'AU', 'Bahamas': 'BS', 'Bahrain': 'BH', 'Bangladesh': 'BD', 'Barbados': 'BB', 'Belgien': 'BE', 'Belize': 'BZ', 'Benin': 'BJ', 'Bermudas': 'BM', 'Bhutan': 'BT', 'Birma': 'MM', 'Bolivien': 'BO', 'Bosnien-Herzegowina': 'BA', 'Botswana': 'BW', 'Bouvet Inseln': 'BV', 'Brasilien': 'BR', 'Britisch-Indischer Ozean': 'IO', 'Brunei': 'BN', 'Bulgarien': 'BG', 'Burkina Faso': 'BF', 'Burundi': 'BI', 'Chile': 'CL', 'China': 'CN', 'Christmas Island': 'CX', 'Cook Inseln': 'CK', 'Costa Rica': 'CR', 'Curaçao': 'CW', 'Dänemark': 'DK', 'Demokratische Republik Kongo': 'CD', 'Deutschland': 'DE', 'Djibuti': 'DJ', 'Dominika': 'DM', 'Dominikanische Republik': 'DO', 'Ecuador': 'EC', 'El Salvador': 'SV', 'Elfenbeinküste': 'CI', 'Eritrea': 'ER', 'Estland': 'EE', 'Falkland Inseln': 'FK', 'Färöer Inseln': 'FO', 'Fidschi': 'FJ', 'Finnland': 'FI', 'Frankreich': 'FR', 'französisch Guyana': 'GF', 'Französisch Polynesien': 'PF', 'Französisches Süd-Territorium': 'TF', 'Gabun': 'GA', 'Gambia': 'GM', 'Georgien': 'GE', 'Ghana': 'GH', 'Gibraltar': 'GI', 'Grenada': 'GD', 'Griechenland': 'GR', 'Grönland': 'GL', 'Großbritannien': 'GB', 'Guadeloupe': 'GP', 'Guam': 'GU', 'Guatemala': 'GT', 'Guernsey': 'GG', 'Guinea': 'GN', 'Guinea Bissau': 'GW', 'Guyana': 'GY', 'Haiti': 'HT', 'Heard und McDonald Islands': 'HM', 'Honduras': 'HN', 'Hong Kong': 'HK', 'Indien': 'IN', 'Indonesien': 'ID', 'Irak': 'IQ', 'Iran': 'IR', 'Irland': 'IE', 'Island': 'IS', 'Isle of Man': 'IM', 'Israel': 'IL', 'Italien': 'IT', 'Jamaika': 'JM', 'Japan': 'JP', 'Jemen': 'YE', 'Jersey': 'JE', 'Jordanien': 'JO', 'Kaiman Inseln': 'KY', 'Kambodscha': 'KH', 'Kamerun': 'CM', 'Kanada': 'CA', 'Kap Verde': 'CV', 'Karibische Niederlande': 'BQ', 'Kasachstan': 'KZ', 'Kenia': 'KE', 'Kirgisistan': 'KG', 'Kiribati': 'KI', 'Kokosinseln': 'CC', 'Kolumbien': 'CO', 'Komoren': 'KM', 'Kongo': 'CG', 'Kroatien': 'HR', 'Kuba': 'CU', 'Kuwait': 'KW', 'Laos': 'LA', 'Lesotho': 'LS', 'Lettland': 'LV', 'Libanon': 'LB', 'Liberia': 'LR', 'Libyen': 'LY', 'Liechtenstein': 'LI', 'Litauen': 'LT', 'Luxemburg': 'LU', 'Macao': 'MO', 'Madagaskar': 'MG', 'Malawi': 'MW', 'Malaysia': 'MY', 'Malediven': 'MV', 'Mali': 'ML', 'Malta': 'MT', 'Marianen': 'MP', 'Marokko': 'MA', 'Marshall Inseln': 'MH', 'Martinique': 'MQ', 'Mauretanien': 'MR', 'Mauritius': 'MU', 'Mayotte': 'YT', 'Mazedonien': 'MK', 'Mexiko': 'MX', 'Mikronesien': 'FM', 'Mocambique': 'MZ', 'Moldavien': 'MD', 'Monaco': 'MC', 'Mongolei': 'MN', 'Montenegro': 'ME', 'Montserrat': 'MS', 'Namibia': 'NA', 'Nauru': 'NR', 'Nepal': 'NP', 'Neukaledonien': 'NC', 'Neuseeland': 'NZ', 'Nicaragua': 'NI', 'Niederlande': 'NL', 'Niger': 'NE', 'Nigeria': 'NG', 'Niue': 'NU', 'Nord Korea': 'KP', 'Norfolk Inseln': 'NF', 'Norwegen': 'NO', 'Oman': 'OM', 'Österreich': 'AT', 'Osttimor': 'TL', 'Pakistan': 'PK', 'Palästina': 'PS', 'Palau': 'PW', 'Panama': 'PA', 'Papua Neuguinea': 'PG', 'Paraguay': 'PY', 'Peru': 'PE', 'Philippinen': 'PH', 'Pitcairn': 'PN', 'Polen': 'PL', 'Portugal': 'PT', 'Puerto Rico': 'PR', 'Qatar': 'QA', 'Reunion': 'RE', 'Ruanda': 'RW', 'Rumänien': 'RO', 'Russland': 'RU', 'Saint Lucia': 'LC', 'Saint-Barthélemy': 'BL', 'Saint-Martin': 'MF', 'Sambia': 'ZM', 'Samoa': 'WS', 'San Marino': 'SM', 'Sao Tome': 'ST', 'Saudi Arabien': 'SA', 'Schweden': 'SE', 'Schweiz': 'CH', 'Senegal': 'SN', 'Serbien': 'RS', 'Seychellen': 'SC', 'Sierra Leone': 'SL', 'Singapur': 'SG', 'Sint Maarten': 'SX', 'Slowakei': 'SK', 'Slowenien': 'SI', 'Solomon Inseln': 'SB', 'Somalia': 'SO', 'Spanien': 'ES', 'Sri Lanka': 'LK', 'St. Helena': 'SH', 'St. Kitts Nevis Anguilla': 'KN', 'St. Pierre und Miquelon': 'PM', 'St. Vincent': 'VC', 'Süd Korea': 'KR', 'Südafrika': 'ZA', 'Sudan': 'SD', 'Südgeorgien und die Südlichen Sandwichinseln': 'GS', 'Südsudan': 'SS', 'Surinam': 'SR', 'Svalbard und Jan Mayen Islands': 'SJ', 'Swasiland': 'SZ', 'Syrien': 'SY', 'Tadschikistan': 'TJ', 'Taiwan': 'TW', 'Tansania': 'TZ', 'Thailand': 'TH', 'Togo': 'TG', 'Tokelau': 'TK', 'Tonga': 'TO', 'Trinidad Tobago': 'TT', 'Tschad': 'TD', 'Tschechische Republik': 'CZ', 'Tunesien': 'TN', 'Türkei': 'TR', 'Turkmenistan': 'TM', 'Turks und Kaikos Inseln': 'TC', 'Tuvalu': 'TV', 'Uganda': 'UG', 'Ukraine': 'UA', 'Ungarn': 'HU', 'United States Minor Outlying Islands': 'UM', 'Uruguay': 'UY', 'Usbekistan': 'UZ', 'Vanuatu': 'VU', 'Vatikan': 'VA', 'Venezuela': 'VE', 'Vereinigte Arabische Emirate': 'AE', 'Vereinigte Staaten von Amerika': 'US', 'Vietnam': 'VN', 'Virgin Island (Brit.)': 'VG', 'Virgin Island (USA)': 'VI', 'Wallis et Futuna': 'WF', 'Weissrussland': 'BY', 'Westsahara': 'EH', 'Zentralafrikanische Republik': 'CF', 'Zimbabwe': 'ZW', 'Zypern': 'CY', 'name': 'alpha-2', 'Albania': 'AL', 'Algeria': 'DZ', 'American Samoa': 'AS', 'Antarctica': 'AQ', 'Antigua and Barbuda': 'AG', 'Argentina': 'AR', 'Armenia': 'AM', 'Australia': 'AU', 'Austria': 'AT', 'Azerbaijan': 'AZ', 'Belarus': 'BY', 'Belgium': 'BE', 'Bermuda': 'BM', 'Bolivia (Plurinational State of)': 'BO', 'Bonaire, Sint Eustatius and Saba': 'BQ', 'Bosnia and Herzegovina': 'BA', 'Bouvet Island': 'BV', 'Brazil': 'BR', 'British Indian Ocean Territory': 'IO', 'Brunei Darussalam': 'BN', 'Bulgaria': 'BG', 'Cabo Verde': 'CV', 'Cambodia': 'KH', 'Cameroon': 'CM', 'Canada': 'CA', 'Cayman Islands': 'KY', 'Central African Republic': 'CF', 'Chad': 'TD', 'Cocos (Keeling) Islands': 'CC', 'Colombia': 'CO', 'Comoros': 'KM', 'Congo': 'CG', 'Congo, Democratic Republic of the': 'CD', 'Cook Islands': 'CK', "Côte d'Ivoire": 'CI', 'Croatia': 'HR', 'Cuba': 'CU', 'Cyprus': 'CY', 'Czechia': 'CZ', 'Denmark': 'DK', 'Djibouti': 'DJ', 'Dominica': 'DM', 'Dominican Republic': 'DO', 'Egypt': 'EG', 'Equatorial Guinea': 'GQ', 'Estonia': 'EE', 'Eswatini': 'SZ', 'Ethiopia': 'ET', 'Falkland Islands (Malvinas)': 'FK', 'Faroe Islands': 'FO', 'Fiji': 'FJ', 'Finland': 'FI', 'France': 'FR', 'French Guiana': 'GF', 'French Polynesia': 'PF', 'French Southern Territories': 'TF', 'Gabon': 'GA', 'Georgia': 'GE', 'Germany': 'DE', 'Greece': 'GR', 'Greenland': 'GL', 'Guinea-Bissau': 'GW', 'Heard Island and McDonald Islands': 'HM', 'Holy See': 'VA', 'Hungary': 'HU', 'Iceland': 'IS', 'India': 'IN', 'Indonesia': 'ID', 'Iran (Islamic Republic of)': 'IR', 'Iraq': 'IQ', 'Ireland': 'IE', 'Italy': 'IT', 'Jamaica': 'JM', 'Jordan': 'JO', 'Kazakhstan': 'KZ', 'Kenya': 'KE', "Korea (Democratic People's Republic of)": 'KP', 'Korea, Republic of': 'KR', 'Kyrgyzstan': 'KG', "Lao People's Democratic Republic": 'LA', 'Latvia': 'LV', 'Lebanon': 'LB', 'Libya': 'LY', 'Lithuania': 'LT', 'Luxembourg': 'LU', 'Madagascar': 'MG', 'Maldives': 'MV', 'Marshall Islands': 'MH', 'Mauritania': 'MR', 'Mexico': 'MX', 'Micronesia (Federated States of)': 'FM', 'Moldova, Republic of': 'MD', 'Mongolia': 'MN', 'Morocco': 'MA', 'Mozambique': 'MZ', 'Myanmar': 'MM', 'Netherlands': 'NL', 'New Caledonia': 'NC', 'New Zealand': 'NZ', 'Norfolk Island': 'NF', 'North Macedonia': 'MK', 'Northern Mariana Islands': 'MP', 'Norway': 'NO', 'Palestine, State of': 'PS', 'Papua New Guinea': 'PG', 'Philippines': 'PH', 'Poland': 'PL', 'Réunion': 'RE', 'Romania': 'RO', 'Russian Federation': 'RU', 'Rwanda': 'RW', 'Saint Barthélemy': 'BL', 'Saint Helena, Ascension and Tristan da Cunha': 'SH', 'Saint Kitts and Nevis': 'KN', 'Saint Martin (French part)': 'MF', 'Saint Pierre and Miquelon': 'PM', 'Saint Vincent and the Grenadines': 'VC', 'Sao Tome and Principe': 'ST', 'Saudi Arabia': 'SA', 'Serbia': 'RS', 'Seychelles': 'SC', 'Singapore': 'SG', 'Sint Maarten (Dutch part)': 'SX', 'Slovakia': 'SK', 'Slovenia': 'SI', 'Solomon Islands': 'SB', 'South Africa': 'ZA', 'South Georgia and the South Sandwich Islands': 'GS', 'South Sudan': 'SS', 'Spain': 'ES', 'Suriname': 'SR', 'Svalbard and Jan Mayen': 'SJ', 'Sweden': 'SE', 'Switzerland': 'CH', 'Syrian Arab Republic': 'SY', 'Taiwan, Province of China': 'TW', 'Tajikistan': 'TJ', 'Tanzania, United Republic of': 'TZ', 'Timor-Leste': 'TL', 'Trinidad and Tobago': 'TT', 'Tunisia': 'TN', 'Turkey': 'TR', 'Turks and Caicos Islands': 'TC', 'United Arab Emirates': 'AE', 'United Kingdom of Great Britain and Northern Ireland': 'GB', 'United States of America': 'US', 'Uzbekistan': 'UZ', 'Venezuela (Bolivarian Republic of)': 'VE', 'Viet Nam': 'VN', 'Virgin Islands (British)': 'VG', 'Virgin Islands (U.S.)': 'VI', 'Wallis and Futuna': 'WF', 'Western Sahara': 'EH', 'Yemen': 'YE', 'Zambia': 'ZM'}