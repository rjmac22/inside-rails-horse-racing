"""Reusable course and candidate-jurisdiction mapping rules.

Extracted from the settled implementation validated in Notebook 04.
Raw source values remain unchanged; derived values remain candidate mappings
with explicit evidence labels.
"""

from __future__ import annotations

import re

import pandas as pd

terminal_code_pattern = re.compile('\\s+\\(([^()]+)\\)$')

recognised_terminal_jurisdiction_codes = {'SWI', 'IRE', 'URU', 'ITY', 'BRZ', 'SWE', 'ARG', 'SPA', 'PER', 'UAE', 'JER', 'NZ', 'JPN', 'GUE', 'TUR', 'CZE', 'POL', 'KSA', 'NOR', 'CHN', 'BEL', 'SIN', 'SAF', 'USA', 'GER', 'FR', 'AUS', 'HK', 'QA', 'DEN', 'CAN', 'CHI', 'KOR', 'BHR', 'HUN'}


terminal_code_to_jurisdiction = {'ARG': 'Argentina', 'AUS': 'Australia', 'BEL': 'Belgium', 'BHR': 'Bahrain', 'BRZ': 'Brazil', 'CAN': 'Canada', 'CHI': 'Chile', 'CHN': 'China', 'CZE': 'Czech Republic', 'DEN': 'Denmark', 'FR': 'France', 'GER': 'Germany', 'GUE': 'Guernsey', 'HK': 'Hong Kong', 'HUN': 'Hungary', 'IRE': 'Ireland', 'ITY': 'Italy', 'JER': 'Jersey', 'JPN': 'Japan', 'KOR': 'South Korea', 'KSA': 'Saudi Arabia', 'NOR': 'Norway', 'NZ': 'New Zealand', 'PER': 'Peru', 'POL': 'Poland', 'QA': 'Qatar', 'SAF': 'South Africa', 'SIN': 'Singapore', 'SPA': 'Spain', 'SWE': 'Sweden', 'SWI': 'Switzerland', 'TUR': 'Turkey', 'UAE': 'United Arab Emirates', 'URU': 'Uruguay', 'USA': 'United States'}


historical_course_to_code = {'Abu Dhabi': 'UAE', 'Aqueduct': 'USA', 'Auteuil': 'FR', 'Baden-Baden': 'GER', 'Bahrain': 'BHR', 'Ballinrobe': 'IRE', 'Bellewstown': 'IRE', 'Belmont Park (Perth)': 'AUS', 'Bendigo': 'AUS', 'Bordeaux Le Bouscat': 'FR', 'Cagnes-Sur-Mer': 'FR', 'Camden (South Carolina)': 'USA', 'Canberra': 'AUS', 'Capannelle': 'ITY', 'Caulfield': 'AUS', 'Chantilly': 'FR', 'Chukyo': 'JPN', 'Churchill Downs': 'USA', 'Cidade Jardim': 'BRZ', 'Clonmel': 'IRE', 'Club Hipico de Santiago': 'CHI', 'Cologne': 'GER', 'Colonial Downs': 'USA', 'Compiegne': 'FR', 'Cork': 'IRE', 'Curragh': 'IRE', 'Deauville': 'FR', 'Del Mar': 'USA', 'Doha': 'QA', 'Doomben': 'AUS', 'Dortmund': 'GER', 'Down Royal': 'IRE', 'Downpatrick': 'IRE', 'Dundalk (AW)': 'IRE', 'Dusseldorf': 'GER', 'Eagle Farm': 'AUS', 'Ellerslie': 'NZ', 'Fair Grounds': 'USA', 'Fairyhouse': 'IRE', 'Far Hills': 'USA', 'Flemington': 'AUS', 'Fontainebleau': 'FR', 'Fukushima': 'JPN', 'Galway': 'IRE', 'Gavea': 'BRZ', 'Geelong': 'AUS', 'Gold Coast': 'AUS', 'Gosford': 'AUS', 'Gowran Park': 'IRE', 'Great Meadow': 'USA', 'Gulfstream Park': 'USA', 'Hanover': 'GER', 'Hanshin': 'JPN', 'Happy Valley': 'HK', 'Hawkesbury': 'AUS', 'Hipodromo Chile': 'CHI', 'Hobart': 'AUS', 'Hoppegarten': 'GER', 'Jebel Ali': 'UAE', 'Keeneland': 'USA', 'Kembla Grange': 'AUS', 'Kenilworth': 'SAF', 'Kilbeggan': 'IRE', 'Killarney': 'IRE', 'Kokura': 'JPN', 'Krefeld': 'GER', 'Kyoto': 'JPN', 'La Plata': 'ARG', 'La Teste De Buch': 'FR', 'Launceston': 'AUS', 'Laurel Park': 'USA', "Le Lion-D'Angers": 'FR', 'Leopardstown': 'IRE', 'Les Landes': 'JER', 'Limerick': 'IRE', 'Lone Star Park': 'USA', 'Longchamp': 'FR', 'Los Alamitos': 'USA', 'Lyon Parilly': 'FR', 'Maronas': 'URU', 'Marseille Borely': 'FR', 'Marseille Pont-de-Vivaux': 'FR', 'Matamata': 'NZ', 'Meydan': 'UAE', 'Monterrico': 'PER', 'Montpelier': 'USA', 'Moonee Valley': 'AUS', 'Morphettville': 'AUS', 'Munich': 'GER', 'Naas': 'IRE', 'Nakayama': 'JPN', 'Nantes': 'FR', 'Navan': 'IRE', 'Niigata': 'JPN', 'Northam': 'AUS', 'Oaklawn Park': 'USA', 'Ohi': 'JPN', 'Pakenham': 'AUS', 'Palermo': 'ARG', 'Pau': 'FR', 'Percy Warner Park': 'USA', 'Punchestown': 'IRE', 'Randwick': 'AUS', 'Riccarton Park': 'NZ', 'Riyadh': 'KSA', 'Roscommon': 'IRE', 'Rosehill': 'AUS', 'Saint-Cloud': 'FR', 'Sam Houston': 'USA', 'San Isidro': 'ARG', 'San Siro': 'ITY', 'Santa Anita': 'USA', 'Scone': 'AUS', 'Scottsville': 'SAF', 'Sha Tin': 'HK', 'Sharjah': 'UAE', 'Sligo': 'IRE', 'St Moritz': 'SWI', 'Strasbourg': 'FR', 'Sunland Park': 'USA', 'Tampa Bay Downs': 'USA', 'Te Rapa': 'NZ', 'Thurles': 'IRE', 'Tokyo': 'JPN', 'Toulouse': 'FR', 'Tramore': 'IRE', 'Trentham': 'NZ', 'Turffontein Standside': 'SAF', 'Turfway Park': 'USA', 'Valparaiso Sporting Club': 'CHI', 'Vichy': 'FR', 'Wexford': 'IRE', 'Woodbine': 'CAN'}


curated_british_course_configurations = {'Lingfield (AW)', 'Newcastle (AW)', 'Southwell (AW)', 'Chelmsford (AW)', 'Wolverhampton (AW)', 'Kempton (AW)', 'Newmarket (July)'}


established_unsuffixed_british_courses = {'Chester', 'Bangor-on-Dee', 'Cartmel', 'Uttoxeter', 'Yarmouth', 'Hereford', 'Redcar', 'Huntingdon', 'Warwick', 'Fakenham', 'Pontefract', 'Ripon', 'Wincanton', 'Goodwood', 'Chepstow', 'Towcester', 'Ascot', 'Windsor', 'Ayr', 'Lingfield', 'Epsom', 'Newton Abbot', 'Beverley', 'Hamilton', 'Plumpton', 'Perth', 'Exeter', 'Southwell', 'Doncaster', 'Market Rasen', 'Kempton', 'Nottingham', 'Kelso', 'Wetherby', 'Salisbury', 'Aintree', 'Worcester', 'Carlisle', 'Haydock', 'Bath', 'Thirsk', 'Stratford', 'Ludlow', 'Ffos Las', 'Newmarket', 'Musselburgh', 'Hexham', 'Leicester', 'Brighton', 'Catterick', 'Taunton', 'Newcastle', 'Cheltenham', 'Sandown', 'Newbury', 'York', 'Sedgefield', 'Fontwell'}


def extract_terminal_jurisdiction_code(course_name):
    """Return a recognised terminal jurisdiction code, otherwise None."""
    match = terminal_code_pattern.search(str(course_name))

    if match and match.group(1) in recognised_terminal_jurisdiction_codes:
        return match.group(1)

    return None


def derive_candidate_race_jurisdiction(row):
    """Derive candidate jurisdiction and retain the supporting rule."""
    course_name = str(row["course"])
    race_date = str(row["date"])
    race_type = str(row["type"])
    race_name = str(row["race_name"])

    terminal_code = extract_terminal_jurisdiction_code(course_name)

    if terminal_code is not None:
        return pd.Series(
            [
                terminal_code_to_jurisdiction[terminal_code],
                "explicit_terminal_course_code",
            ]
        )

    if course_name in historical_course_to_code:
        historical_code = historical_course_to_code[course_name]

        return pd.Series(
            [
                terminal_code_to_jurisdiction[historical_code],
                "historical_suffixed_course_link",
            ]
        )

    if course_name in curated_british_course_configurations:
        return pd.Series(
            [
                "Great Britain",
                "curated_british_course_configuration",
            ]
        )

    if course_name == "Firenze":
        return pd.Series(
            [
                "Italy",
                "curated_venue_reference",
            ]
        )

    if course_name == "Ascot":
        if (
            race_date >= "2025-10-15"
            and race_type == "Flat"
            and "(Turf)" in race_name
        ):
            return pd.Series(
                [
                    "Australia",
                    "race_context_course_collision_rule",
                ]
            )

        return pd.Series(
            [
                "Great Britain",
                "race_context_course_collision_rule",
            ]
        )

    if course_name == "Newcastle":
        if (
            race_date >= "2025-10-15"
            and race_type == "Flat"
            and "(Turf)" in race_name
        ):
            return pd.Series(
                [
                    "Australia",
                    "race_context_course_collision_rule",
                ]
            )

        return pd.Series(
            [
                "Great Britain",
                "race_context_course_collision_rule",
            ]
        )

    if course_name == "Sandown":
        return pd.Series(
            [
                "Great Britain",
                "race_context_course_collision_rule",
            ]
        )

    if course_name in established_unsuffixed_british_courses:
        return pd.Series(
            [
                "Great Britain",
                "established_unsuffixed_british_course",
            ]
        )

    return pd.Series(
        [
            "unresolved",
            "no_established_jurisdiction_evidence",
        ]
    )




def derive_candidate_course_label(course_name):
    """Remove only a recognised terminal jurisdiction suffix."""
    course_text = str(course_name)
    terminal_code = extract_terminal_jurisdiction_code(course_text)

    if terminal_code is None:
        return course_text

    return terminal_code_pattern.sub("", course_text).rstrip()
