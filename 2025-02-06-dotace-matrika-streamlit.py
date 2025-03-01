import streamlit as st
import pandas as pd
from src.matrikadb import connect_to_db

st.set_page_config(
    page_title="SPORTOVCI ČBS", page_icon="♣️", layout="wide"
)

# Load data
@st.cache_data
def load_data():
    credentials = {
        "server": st.secrets["MATRIKA_DB_SERVER"],
        "database": st.secrets["MATRIKA_DB_NAME"],
        "username": st.secrets["MATRIKA_DB_USERNAME"],
        "password": st.secrets["MATRIKA_DB_PASSWORD"],
    }

    conn = connect_to_db(**credentials)
    ucasti_sql = """
    SELECT 
        h.Legitimace,
        h.Prijmeni,
        h.Jmena,
        h.Rocnik,
        k.Nazev as KlubNazev,
        t.Id as TurnajId,
        t.Nazev as TurnajNazev,
        t.DatumOd as TurnajOd,
        t.DatumDo as TurnajDo,
        kt.Nazev as KategorieTurnaje,
        CASE 
            WHEN p.Id IS NOT NULL THEN 'Ano'
            ELSE 'Ne'
        END as ClenPrispevek2024,
        COALESCE(r._AktualniKB, 0) as Body,
        COALESCE(r.Poradi, 0) as PoradiVZebricku,
        dbo.GetKategorieHrace(h.Rocnik, h.PohlaviM, null) as Kategorie
    FROM Hrac h
    INNER JOIN Ucast u ON h.Legitimace = u.IdHrace
    INNER JOIN Soutezici s ON s.Id = u.IdSouteziciho
    INNER JOIN Turnaj t ON t.Id = s.IdTurnaje
    LEFT JOIN Klub k ON k.Id = h.IdKlubu
    LEFT JOIN KategorieTurnaje kt ON kt.Id = t.IdKategorie
    LEFT JOIN Prispevek p ON p.IdHrace = h.Legitimace AND p.IdSezony = 2024
    LEFT JOIN vRanking r ON r.Legitimace = h.Legitimace
    WHERE 
        t.DatumOd >= CONVERT(datetime, '2023-11-01', 120)
        AND t.DatumOd <= CONVERT(datetime, '2024-10-31', 120)
    ORDER BY Prijmeni, Jmena
    """
    df = pd.read_sql(ucasti_sql, conn)

    # Calculate tournament duration
    df["DobaTurnaje"] = (
        pd.to_datetime(df["TurnajDo"]) - pd.to_datetime(df["TurnajOd"])
    ).dt.days
    df.loc[df["DobaTurnaje"] == 0, "DobaTurnaje"] = 1

    # Manual adjustments for long tournaments

    long_tournament_mapping = {
        "Skupinovka České Budějovice - Jaro 2024": 6,
        "Skupinovka České Budějovice - Podzim 2024": 6,
        "Pražská skupinová A zima 2023": 5,
        "1. Liga 2024": 8,
        "Skupinová A - Jaro 2024": 5,
        "Pražská skupinová A léto 2024": 5,
        "Pražská skupinovka A Jaro 2024": 5,
        "Pražská liga jaro 2024": 10,
        "Skupinová A Podzim 2024": 5,
        "2. Liga 2024": 8,
        "Skupinová B Podzim 2024": 9,
        "Pražská Skupinová B Jaro 2024": 9,
        "Pražská švýcarská skupinovka jaro 2024": 5,
        "Švýcarská skupinovka podzim 2024": 5,
        "Brno skupinovka 09/24 - 01/25": 6,
        "Brno - Skupinovka": 6,
    }

    # Upravíme počet dnů soutěží pro dlouhodobé turnaje
    for tournament, days in long_tournament_mapping.items():
        df.loc[df["TurnajNazev"] == tournament, "DobaTurnaje"] = days

    # Zobrazime mapovani
    for tournament, days in long_tournament_mapping.items():
        print(f"{tournament}".ljust(45), f"{days} dní")

    for tournament, days in long_tournament_mapping.items():
        df.loc[df["TurnajNazev"] == tournament, "DobaTurnaje"] = days

    return df


def format_points(kb_points):
    if pd.isna(kb_points):
        return ""

    kb = int(kb_points % 1000)
    sb = int((kb_points // 1000) % 100)
    zb = int(kb_points // 100000)

    parts = []
    parts.append(f"{zb:2d} ZB")
    parts.append(f"{sb:2d} SB")
    parts.append(f"{kb:3d} KB")

    return " ".join(parts)


def split_points(kb_points):
    if pd.isna(kb_points):
        return 0, 0, 0

    kb = int(kb_points % 1000)
    sb = int((kb_points // 1000) % 100)
    zb = int(kb_points // 100000)

    return zb, sb, kb


try:
    df = load_data()

    # Filter out unwanted categories and non-members
    df = df[
        (~df["KategorieTurnaje"].isin(["Funbridge", "Klubové a jiné podobné turnaje"]))
        & (df["KategorieTurnaje"].notna())
        & (df["ClenPrispevek2024"] == "Ano")
    ]

    # Group by player and calculate total days
    sportovci_dny = (
        df.groupby(
            [
                "Legitimace",
                "Prijmeni",
                "Jmena",
                "Rocnik",
                "KlubNazev",
                "Body",
                "PoradiVZebricku",
                "Kategorie",
            ]
        )["DobaTurnaje"]
        .sum()
        .reset_index()
        .rename(columns={"DobaTurnaje": "Pocet dni"})
    )

    # Filter players with more than 6 days
    sportovci_nad_6_dni = sportovci_dny[sportovci_dny["Pocet dni"] >= 6].sort_values(
        "Pocet dni", ascending=False
    )
    
    # Check if we're in "show participations" mode via URL
    params = st.query_params
    show_player = params.get('select', None)
    


    if show_player:
        try:
            legitimace = int(show_player)
            # Show only participations for selected player
            participations_df = df[
                ['Legitimace', 'Prijmeni', 'Jmena', 'KlubNazev', 'TurnajId', 'TurnajNazev', 'TurnajOd', 'TurnajDo', 'KategorieTurnaje', 'DobaTurnaje']
            ].sort_values(['TurnajOd'])
            
            participations_df = participations_df[participations_df['Legitimace'] == legitimace]
            
            # st.button("Zpět n hlavní report", on_click=st.query_params.clear)
            
            if not participations_df.empty:
                player = participations_df.iloc[0]
                st.title(f"Účasti hráče: {player['Prijmeni']} {player['Jmena']} ({player['Legitimace']})")
                st.link_button("Zobrazit detail hráče v matrice", f"https://matrikacbs.cz/Detail-hrace.aspx?id={legitimace}")
                
                # Convert dates to more readable format
                participations_df['TurnajOd'] = pd.to_datetime(participations_df['TurnajOd']).dt.strftime('%d.%m.%Y')
                participations_df['TurnajDo'] = pd.to_datetime(participations_df['TurnajDo']).dt.strftime('%d.%m.%Y')
                
                # Add tournament link column
                participations_df['TurnajLink'] = participations_df['TurnajId'].apply(
                    lambda x: f"https://matrikacbs.cz/Detail-turnaje.aspx?id={x}"
                )
                
                # Reorder columns to put TurnajLink right after TurnajNazev
                cols = ['TurnajNazev', 'TurnajLink', 'TurnajOd', 'TurnajDo', 'KategorieTurnaje', 'DobaTurnaje']
                participations_df = participations_df[cols]
                
                st.dataframe(
                    participations_df,
                    column_config={
                        "TurnajNazev": "Turnaj",
                        "TurnajLink": st.column_config.LinkColumn(
                            "Detail turnaje",
                            help="Odkaz na detail turnaje v matrice",
                            display_text="Zobrazit v matrice",
                            validate="^https://.*"
                        ),
                        "TurnajOd": "Od",
                        "TurnajDo": "Do",
                        "KategorieTurnaje": "Kategorie turnaje",
                        "DobaTurnaje": st.column_config.NumberColumn(
                            "Počet dní",
                            help="Počet dní turnaje",
                            format="%d"
                        )
                    },
                    hide_index=True,
                    height=500
                )
            else:
                st.error("Hráč nenalezen")
        except ValueError:
            st.error("Neplatné číslo legitimace")
    else:
    
        # Show full application
        # Title
        # Page config

        # Title
        st.title("Report registrovaných sportovců Českého bridžového svazu")
        st.markdown("""
        Tento report zobrazuje seznam sportovců, kteří se zúčastnili více než 6 dnů soutěží 
        v období od 1.11.2023 do 30.10.2024.
        
        Data jsou načtena z matriky Českého bridžového svazu, která je dostupná na adrese https://matrikacbs.cz/

        Soutěže jsou filtrovány podle kategorie a počet dnů soutěží je počítán pomocí pole DatumOd a DatumDo v matrice, kde vícetermínové soutěže jsou upraveny ručně.
        """)
        
        # Sidebar filters
        st.sidebar.header("Filtry")

        min_rok = int(sportovci_nad_6_dni["Rocnik"].min())
        max_rok = int(sportovci_nad_6_dni["Rocnik"].max())

        rok_od, rok_do = st.sidebar.slider(
            "Rozmezí roků narození:",
            min_value=min_rok,
            max_value=max_rok,
            value=(1975, 2001),
        )

        min_dny = st.sidebar.number_input(
            "Minimální počet dní účasti:", min_value=1, value=6
        )

        kluby = sorted(sportovci_nad_6_dni["KlubNazev"].unique())
        vybrane_kluby = st.sidebar.multiselect(
            "Filtrovat podle klubu:", options=kluby, default=[]
        )

        # Apply filters
        filtered_df = sportovci_nad_6_dni[
            (sportovci_nad_6_dni["Rocnik"] >= rok_od)
            & (sportovci_nad_6_dni["Rocnik"] <= rok_do)
            & (sportovci_nad_6_dni["Pocet dni"] >= min_dny)
        ]

        if vybrane_kluby:
            filtered_df = filtered_df[filtered_df["KlubNazev"].isin(vybrane_kluby)]

        # First create LegitimaceLink column
        display_df = filtered_df.copy()
        display_df["LegitimaceLink"] = display_df["Legitimace"].apply(
            lambda x: f"https://matrikacbs.cz/Detail-hrace.aspx?id={x}"
        )

        # Then remove unwanted columns
        display_df = display_df.drop(columns=["PoradiVZebricku"])

        # Split points into three columns
        display_df[["ZB", "SB", "KB"]] = pd.DataFrame(
            display_df["Body"].apply(split_points).tolist(), index=display_df.index
        )

        # Rename Body to BodyCelkem and move it to the end
        display_df = display_df.rename(columns={"Body": "BodyCelkem"})
        cols = [col for col in display_df.columns if col != "BodyCelkem"] + ["BodyCelkem"]
        display_df = display_df[cols]

        # Display metrics
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Celkový počet sportovců", len(sportovci_nad_6_dni))
        with col2:
            st.metric("Počet filtrovaných sportovců", len(filtered_df))



        # Add selection column with links that open in new tab
        display_df['Vybrat'] = display_df['Legitimace'].apply(
            lambda x: f"?select={x}"
        )

        # Hide Legitimace column and reorder columns
        display_df = display_df.drop(columns=["Legitimace"])
        
        # Create list of columns in desired order
        column_order = [
            "LegitimaceLink",
            "Prijmeni", 
            "Jmena",
            "Rocnik",
            "KlubNazev",
            "Kategorie",
            "Pocet dni",
            "Vybrat",
            "ZB",
            "SB", 
            "KB",
            "BodyCelkem"
        ]
        
        # Reorder columns
        display_df = display_df[column_order]

        # Rest of your original code for the main view...
        st.subheader("Seznam sportovců")
        st.dataframe(
            display_df,
            column_config={
                "LegitimaceLink": st.column_config.LinkColumn(
                    "Legitimace",
                    help="Číslo legitimace hráče (kliknutím zobrazíte detail)",
                    validate="^https://.*",
                    display_text="https://matrikacbs.cz/Detail-hrace.aspx\?id=(.*)",
                    pinned=True
                ),
                "Prijmeni": "Příjmení",
                "Jmena": "Jména",
                "Rocnik": st.column_config.NumberColumn(
                    "Ročník", help="Rok narození", format="%d"
                ),
                "KlubNazev": "Klub",
                "Kategorie": "Kategorie",
                "Pocet dni": st.column_config.NumberColumn(
                    "Počet dní", help="Celkový počet dní účasti na soutěžích", format="%d"
                ),
                "Vybrat": st.column_config.LinkColumn(
                    "Účasti",
                    display_text="Zobrazit účasti",
                    help="Kliknutím zobrazíte účasti vybraného hráče (otevře se v novém okně)"
                ),
                "BodyCelkem": st.column_config.NumberColumn(
                    "Body celkem", help="Celkový počet bodů v KB", format="%d"
                ),
                "ZB": st.column_config.NumberColumn("ZB", help="Zlaté body", format="%2d"),
                "SB": st.column_config.NumberColumn(
                    "SB", help="Stříbrné body", format="%2d"
                ),
                "KB": st.column_config.NumberColumn(
                    "KB", help="Klasifikační body", format="%3d"
                )
            },
            hide_index=True
        )

        # Existing download buttons remain at the end
        csv = filtered_df.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="Stáhnout filtrovaný seznam (CSV)",
            data=csv,
            file_name="sportovci_filtrovani.csv",
            mime="text/csv",
        )

        csv_all = sportovci_nad_6_dni.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="Stáhnout kompletní seznam (CSV)",
            data=csv_all,
            file_name="sportovci_vsichni.csv",
            mime="text/csv",
        )
        
        # After all existing content, add new section
        st.header("Seznam všech účastí")
        
        # Get legitimace numbers from filtered players
        filtered_legitimace = filtered_df['Legitimace'].unique()
        
        # Create participation details DataFrame for filtered players
        all_participations_df = df[
            df['Legitimace'].isin(filtered_legitimace)
        ][['Legitimace', 'Prijmeni', 'Jmena', 'KlubNazev', 'TurnajId', 'TurnajNazev', 'TurnajOd', 'TurnajDo', 'KategorieTurnaje', 'DobaTurnaje']
        ].sort_values(['Prijmeni', 'Jmena', 'TurnajOd'])
        
        # Display metrics
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Celkový počet účastí", len(df[df['Legitimace'].isin(sportovci_nad_6_dni['Legitimace'])]))
        with col2:
            st.metric("Počet filtrovaných účastí", len(all_participations_df))
        
        # Convert dates to more readable format
        all_participations_df['TurnajOd'] = pd.to_datetime(all_participations_df['TurnajOd']).dt.strftime('%d.%m.%Y')
        all_participations_df['TurnajDo'] = pd.to_datetime(all_participations_df['TurnajDo']).dt.strftime('%d.%m.%Y')
        
        # Add tournament link column
        all_participations_df['TurnajLink'] = all_participations_df['TurnajId'].apply(
            lambda x: f"https://matrikacbs.cz/Detail-turnaje.aspx?id={x}"
        )
        
        # Display participations
        st.dataframe(
            all_participations_df,
            column_config={
                "Legitimace": st.column_config.NumberColumn(
                    "Legitimace",
                    help="Číslo legitimace hráče",
                    format="%d"
                ),
                "Prijmeni": "Příjmení",
                "Jmena": "Jména",
                "KlubNazev": "Klub",
                "TurnajNazev": "Turnaj",
                "TurnajLink": st.column_config.LinkColumn(
                    "Detail turnaje",
                    help="Odkaz na detail turnaje v matrice",
                    display_text="zobrazit v matrice",
                    validate="^https://.*"
                ),
                "TurnajOd": "Od",
                "TurnajDo": "Do",
                "KategorieTurnaje": "Kategorie turnaje",
                "DobaTurnaje": st.column_config.NumberColumn(
                    "Počet dní",
                    help="Počet dní turnaje",
                    format="%d"
                )
            },
            hide_index=True
        )
        
        # Add download button for all participations


        st.download_button(
            label="Stáhnout filtrované účasti (CSV)",
            data=filtered_df.to_csv(index=False).encode("utf-8"),
            file_name="vsechny_ucasti.csv",
            mime="text/csv",
        )
        st.download_button(
            label="Stáhnout všechny účasti",
            data=all_participations_df.to_csv(index=False).encode("utf-8"),
            file_name="vsechny_ucasti.csv",
            mime="text/csv",
        )



except Exception as e:
    st.error(f"Nastala chyba při načítání dat: {str(e)}")
