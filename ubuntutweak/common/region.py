#!/usr/bin/env python

# this data get from wikipedia
# http://en.wikipedia.org/wiki/List_of_countries_by_continent_%28data_file%29
REGION_TABLE = """AS AF AFG 004 Afghanistan, Islamic Republic of
EU AX ALA 248 Aland Islands
EU AL ALB 008 Albania, Republic of
AF DZ DZA 012 Algeria, People's Democratic Republic of
OC AS ASM 016 American Samoa
EU AD AND 020 Andorra, Principality of
AF AO AGO 024 Angola, Republic of
NA AI AIA 660 Anguilla
AN AQ ATA 010 Antarctica (the territory South of 60 deg S)
NA AG ATG 028 Antigua and Barbuda
SA AR ARG 032 Argentina, Argentine Republic
AS AM ARM 051 Armenia, Republic of
NA AW ABW 533 Aruba
OC AU AUS 036 Australia, Commonwealth of
EU AT AUT 040 Austria, Republic of
AS AZ AZE 031 Azerbaijan, Republic of
NA BS BHS 044 Bahamas, Commonwealth of the
AS BH BHR 048 Bahrain, Kingdom of
AS BD BGD 050 Bangladesh, People's Republic of
NA BB BRB 052 Barbados
EU BY BLR 112 Belarus, Republic of
EU BE BEL 056 Belgium, Kingdom of
NA BZ BLZ 084 Belize
AF BJ BEN 204 Benin, Republic of
NA BM BMU 060 Bermuda
AS BT BTN 064 Bhutan, Kingdom of
SA BO BOL 068 Bolivia, Republic of
EU BA BIH 070 Bosnia and Herzegovina
AF BW BWA 072 Botswana, Republic of
AN BV BVT 074 Bouvet Island (Bouvetoya)
SA BR BRA 076 Brazil, Federative Republic of
AS IO IOT 086 British Indian Ocean Territory (Chagos Archipelago)
NA VG VGB 092 British Virgin Islands
AS BN BRN 096 Brunei Darussalam
EU BG BGR 100 Bulgaria, Republic of
AF BF BFA 854 Burkina Faso
AF BI BDI 108 Burundi, Republic of
AS KH KHM 116 Cambodia, Kingdom of
AF CM CMR 120 Cameroon, Republic of
NA CA CAN 124 Canada
AF CV CPV 132 Cape Verde, Republic of
NA KY CYM 136 Cayman Islands
AF CF CAF 140 Central African Republic
AF TD TCD 148 Chad, Republic of
SA CL CHL 152 Chile, Republic of
AS CN CHN 156 China, People's Republic of
AS CX CXR 162 Christmas Island
AS CC CCK 166 Cocos (Keeling) Islands
SA CO COL 170 Colombia, Republic of
AF KM COM 174 Comoros, Union of the
AF CD COD 180 Congo, Democratic Republic of the
AF CG COG 178 Congo, Republic of the
OC CK COK 184 Cook Islands
NA CR CRI 188 Costa Rica, Republic of
AF CI CIV 384 Cote d'Ivoire, Republic of
EU HR HRV 191 Croatia, Republic of
NA CU CUB 192 Cuba, Republic of
AS CY CYP 196 Cyprus, Republic of
EU CZ CZE 203 Czech Republic
EU DK DNK 208 Denmark, Kingdom of
AF DJ DJI 262 Djibouti, Republic of
NA DM DMA 212 Dominica, Commonwealth of
NA DO DOM 214 Dominican Republic
SA EC ECU 218 Ecuador, Republic of
AF EG EGY 818 Egypt, Arab Republic of
NA SV SLV 222 El Salvador, Republic of
AF GQ GNQ 226 Equatorial Guinea, Republic of
AF ER ERI 232 Eritrea, State of
EU EE EST 233 Estonia, Republic of
AF ET ETH 231 Ethiopia, Federal Democratic Republic of
EU FO FRO 234 Faroe Islands
SA FK FLK 238 Falkland Islands (Malvinas)
OC FJ FJI 242 Fiji, Republic of the Fiji Islands
EU FI FIN 246 Finland, Republic of
EU FR FRA 250 France, French Republic
SA GF GUF 254 French Guiana
OC PF PYF 258 French Polynesia
AN TF ATF 260 French Southern Territories
AF GA GAB 266 Gabon, Gabonese Republic
AF GM GMB 270 Gambia, Republic of the
AS GE GEO 268 Georgia
EU DE DEU 276 Germany, Federal Republic of
AF GH GHA 288 Ghana, Republic of
EU GI GIB 292 Gibraltar
EU GR GRC 300 Greece, Hellenic Republic
NA GL GRL 304 Greenland
NA GD GRD 308 Grenada
NA GP GLP 312 Guadeloupe
OC GU GUM 316 Guam
NA GT GTM 320 Guatemala, Republic of
EU GG GGY 831 Guernsey, Bailiwick of
AF GN GIN 324 Guinea, Republic of
AF GW GNB 624 Guinea-Bissau, Republic of
SA GY GUY 328 Guyana, Co-operative Republic of
NA HT HTI 332 Haiti, Republic of
AN HM HMD 334 Heard Island and McDonald Islands
EU VA VAT 336 Holy See (Vatican City State)
NA HN HND 340 Honduras, Republic of
AS HK HKG 344 Hong Kong, Special Administrative Region of China
EU HU HUN 348 Hungary, Republic of
EU IS ISL 352 Iceland, Republic of
AS IN IND 356 India, Republic of
AS ID IDN 360 Indonesia, Republic of
AS IR IRN 364 Iran, Islamic Republic of
AS IQ IRQ 368 Iraq, Republic of
EU IE IRL 372 Ireland
EU IM IMN 833 Isle of Man
AS IL ISR 376 Israel, State of
EU IT ITA 380 Italy, Italian Republic
NA JM JAM 388 Jamaica
AS JP JPN 392 Japan
EU JE JEY 832 Jersey, Bailiwick of
AS JO JOR 400 Jordan, Hashemite Kingdom of
AS KZ KAZ 398 Kazakhstan, Republic of
AF KE KEN 404 Kenya, Republic of
OC KI KIR 296 Kiribati, Republic of
AS KP PRK 408 Korea, Democratic People's Republic of
AS KR KOR 410 Korea, Republic of
AS KW KWT 414 Kuwait, State of
AS KG KGZ 417 Kyrgyz Republic
AS LA LAO 418 Lao People's Democratic Republic
EU LV LVA 428 Latvia, Republic of
AS LB LBN 422 Lebanon, Lebanese Republic
AF LS LSO 426 Lesotho, Kingdom of
AF LR LBR 430 Liberia, Republic of
AF LY LBY 434 Libyan Arab Jamahiriya
EU LI LIE 438 Liechtenstein, Principality of
EU LT LTU 440 Lithuania, Republic of
EU LU LUX 442 Luxembourg, Grand Duchy of
AS MO MAC 446 Macao, Special Administrative Region of China
EU MK MKD 807 Macedonia, Republic of
AF MG MDG 450 Madagascar, Republic of
AF MW MWI 454 Malawi, Republic of
AS MY MYS 458 Malaysia
AS MV MDV 462 Maldives, Republic of
AF ML MLI 466 Mali, Republic of
EU MT MLT 470 Malta, Republic of
OC MH MHL 584 Marshall Islands, Republic of the
NA MQ MTQ 474 Martinique
AF MR MRT 478 Mauritania, Islamic Republic of
AF MU MUS 480 Mauritius, Republic of
AF YT MYT 175 Mayotte
NA MX MEX 484 Mexico, United Mexican States
OC FM FSM 583 Micronesia, Federated States of
EU MD MDA 498 Moldova, Republic of
EU MC MCO 492 Monaco, Principality of
AS MN MNG 496 Mongolia
EU ME MNE 499 Montenegro, Republic of
NA MS MSR 500 Montserrat
AF MA MAR 504 Morocco, Kingdom of
AF MZ MOZ 508 Mozambique, Republic of
AS MM MMR 104 Myanmar, Union of
AF NA NAM 516 Namibia, Republic of
OC NR NRU 520 Nauru, Republic of
AS NP NPL 524 Nepal, State of
NA AN ANT 530 Netherlands Antilles
EU NL NLD 528 Netherlands, Kingdom of the
OC NC NCL 540 New Caledonia
OC NZ NZL 554 New Zealand
NA NI NIC 558 Nicaragua, Republic of
AF NE NER 562 Niger, Republic of
AF NG NGA 566 Nigeria, Federal Republic of
OC NU NIU 570 Niue
OC NF NFK 574 Norfolk Island
OC MP MNP 580 Northern Mariana Islands, Commonwealth of the
EU NO NOR 578 Norway, Kingdom of
AS OM OMN 512 Oman, Sultanate of
AS PK PAK 586 Pakistan, Islamic Republic of
OC PW PLW 585 Palau, Republic of
AS PS PSE 275 Palestinian Territory, Occupied
NA PA PAN 591 Panama, Republic of
OC PG PNG 598 Papua New Guinea, Independent State of
SA PY PRY 600 Paraguay, Republic of
SA PE PER 604 Peru, Republic of
AS PH PHL 608 Philippines, Republic of the
OC PN PCN 612 Pitcairn Islands
EU PL POL 616 Poland, Republic of
EU PT PRT 620 Portugal, Portuguese Republic
NA PR PRI 630 Puerto Rico, Commonwealth of
AS QA QAT 634 Qatar, State of
AF RE REU 638 Reunion
EU RO ROU 642 Romania
EU RU RUS 643 Russian Federation
AF RW RWA 646 Rwanda, Republic of
NA BL BLM 652 Saint Barthelemy
AF SH SHN 654 Saint Helena
NA KN KNA 659 Saint Kitts and Nevis, Federation of
NA LC LCA 662 Saint Lucia
NA MF MAF 663 Saint Martin
NA PM SPM 666 Saint Pierre and Miquelon
NA VC VCT 670 Saint Vincent and the Grenadines
OC WS WSM 882 Samoa, Independent State of
EU SM SMR 674 San Marino, Republic of
AF ST STP 678 Sao Tome and Principe, Democratic Republic of
AS SA SAU 682 Saudi Arabia, Kingdom of
AF SN SEN 686 Senegal, Republic of
EU RS SRB 688 Serbia, Republic of
AF SC SYC 690 Seychelles, Republic of
AF SL SLE 694 Sierra Leone, Republic of
AS SG SGP 702 Singapore, Republic of
EU SK SVK 703 Slovakia (Slovak Republic)
EU SI SVN 705 Slovenia, Republic of
OC SB SLB 090 Solomon Islands
AF SO SOM 706 Somalia, Somali Republic
AF ZA ZAF 710 South Africa, Republic of
AN GS SGS 239 South Georgia and the South Sandwich Islands
EU ES ESP 724 Spain, Kingdom of
AS LK LKA 144 Sri Lanka, Democratic Socialist Republic of
AF SD SDN 736 Sudan, Republic of
SA SR SUR 740 Suriname, Republic of
EU SJ SJM 744 Svalbard & Jan Mayen Islands
AF SZ SWZ 748 Swaziland, Kingdom of
EU SE SWE 752 Sweden, Kingdom of
EU CH CHE 756 Switzerland, Swiss Confederation
AS SY SYR 760 Syrian Arab Republic
AS TW TWN 158 Taiwan
AS TJ TJK 762 Tajikistan, Republic of
AF TZ TZA 834 Tanzania, United Republic of
AS TH THA 764 Thailand, Kingdom of
AS TL TLS 626 Timor-Leste, Democratic Republic of
AF TG TGO 768 Togo, Togolese Republic
OC TK TKL 772 Tokelau
OC TO TON 776 Tonga, Kingdom of
NA TT TTO 780 Trinidad and Tobago, Republic of
AF TN TUN 788 Tunisia, Tunisian Republic
AS TR TUR 792 Turkey, Republic of
AS TM TKM 795 Turkmenistan
NA TC TCA 796 Turks and Caicos Islands
OC TV TUV 798 Tuvalu
AF UG UGA 800 Uganda, Republic of
EU UA UKR 804 Ukraine
AS AE ARE 784 United Arab Emirates
EU GB GBR 826 United Kingdom of Great Britain & Northern Ireland
NA US USA 840 United States of America
OC UM UMI 581 United States Minor Outlying Islands
NA VI VIR 850 United States Virgin Islands
SA UY URY 858 Uruguay, Eastern Republic of
AS UZ UZB 860 Uzbekistan, Republic of
OC VU VUT 548 Vanuatu, Republic of
SA VE VEN 862 Venezuela, Bolivarian Republic of
AS VN VNM 704 Vietnam, Socialist Republic of
OC WF WLF 876 Wallis and Futuna
AF EH ESH 732 Western Sahara
AS YE YEM 887 Yemen
AF ZM ZMB 894 Zambia, Republic of
AF ZW ZWE 716 Zimbabwe, Republic of"""

CONTINENT_DICT = {"AF":"Africa",
       "AS":"Asia",
       "EU":"Europe",
       "NA":"North America",
       "SA":"South America",
       "OC":"Oceania",
       "AN":"Antarctica"}
