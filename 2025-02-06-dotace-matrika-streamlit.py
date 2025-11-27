import streamlit as st
import pandas as pd
import pyodbc

debug = True

st.set_page_config(
    page_title="SPORTOVCI ČBS", page_icon="♣️", layout="wide"
)

@st.cache_resource
def init_connection():
    return pyodbc.connect(
        "DRIVER={ODBC Driver 17 for SQL Server};SERVER="
        + st.secrets["server"]
        + ";DATABASE="
        + st.secrets["database"]
        + ";UID="
        + st.secrets["username"]
        + ";TrustServerCertificate=yes"
        + ";Encrypt=yes"
        + ";PWD="
        + st.secrets["password"]
    )
    
conn = init_connection()


@st.cache_data
def load_players(season):
    q = f"""

SELECT DISTINCT
    Jmena, Prijmeni, Legitimace, Rocnik, k.Nazev as KlubNazev,
    dbo.GetKategorieHrace(Rocnik, PohlaviM, null) as Kategorie
FROM [db3206].[dbo].[Prispevek] p
JOIN [db3206].[dbo].[Hrac] ON  Legitimace = p.IdHrace
LEFT JOIN Klub k ON k.Id = IdKlubu
WHERE p.IdSezony = {season}

    """
    df = pd.read_sql(q, conn)
    return df

# Load data
@st.cache_data
def load_data(season):
    # Calculate date range for season (season N runs from Nov 1 of year N-1 to Oct 31 of year N)
    date_from = f"{season - 1}-11-01"
    date_to = f"{season}-10-31"

    ucasti_sql = f"""
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
        COALESCE(t.PocetHracichDni, 1) as DobaTurnaje,
        kt.Nazev as KategorieTurnaje,
        CASE 
            WHEN p.Id IS NOT NULL THEN 'Ano'
            ELSE 'Ne'
        END as ClenPrispevek2025,
        COALESCE(r._AktualniKB, 0) as Body,
        COALESCE(r.Poradi, 0) as PoradiVZebricku,
        dbo.GetKategorieHrace(h.Rocnik, h.PohlaviM, null) as Kategorie
    FROM Hrac h
    LEFT JOIN Ucast u ON h.Legitimace = u.IdHrace
    INNER JOIN Soutezici s ON s.Id = u.IdSouteziciho
    INNER JOIN Turnaj t ON t.Id = s.IdTurnaje
    LEFT JOIN Klub k ON k.Id = h.IdKlubu
    LEFT JOIN KategorieTurnaje kt ON kt.Id = t.IdKategorie
    LEFT JOIN Prispevek p ON p.IdHrace = h.Legitimace AND p.IdSezony = {season}
    LEFT JOIN vRanking r ON r.Legitimace = h.Legitimace
    WHERE 
        t.DatumOd >= CONVERT(datetime, '{date_from}', 120)
        AND t.DatumOd <= CONVERT(datetime, '{date_to}', 120)
    ORDER BY Prijmeni, Jmena
    """
    df = pd.read_sql(ucasti_sql, conn)
    
    # Fill NA for kategorie
    df["KategorieTurnaje"] = df["KategorieTurnaje"].fillna("Bez kategorie")

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
    # Season selector (before loading data)
    st.sidebar.header("Nastavení sezóny")
    selected_season = st.sidebar.selectbox(
        "Vyberte sezónu:",
        options=[2026, 2025, 2024],
        index=1
    )
    
    df = load_data(selected_season)




    
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
        
        # Calculate date range for display
        date_from_display = f"1.11.{selected_season - 1}"
        date_to_display = f"30.10.{selected_season}"
        
        st.markdown(f"""
        Tento report zobrazuje seznam sportovců, kteří se zúčastnili více než 6 dnů soutěží 
        v období od {date_from_display} do {date_to_display} a mají zaplacené příspěvky za rok {selected_season}.
        
        Data jsou načtena z matriky Českého bridžového svazu, která je dostupná na adrese https://matrikacbs.cz/

        Soutěže jsou filtrovány podle kategorie a počet dnů soutěží je počítán pomocí pole DatumOd a DatumDo v matrice, kde vícetermínové soutěže jsou upraveny ručně.
        """)
        
        # Sidebar filters
        st.sidebar.header("Filtry")

        min_rok = int(df["Rocnik"].min())
        max_rok = int(df["Rocnik"].max())

        rok_od, rok_do = st.sidebar.slider(
            "Rozmezí roků narození:",
            min_value=min_rok,
            max_value=max_rok,
            value=(min_rok, max_rok),
        )

        min_dny = st.sidebar.number_input(
            "Minimální počet dní účasti:", min_value=1, value=6
        )

        kluby = sorted(df["KlubNazev"].unique())
        vybrane_kluby = st.sidebar.multiselect(
            "Filtrovat podle klubu:",
            options=kluby,
            default=[]
        )
        
        only_with_prispevek = st.sidebar.checkbox(
            "Filtrovat pouze sportovce s členským příspěvkem",
            value=True
        )

        kategorie_turnaju = sorted([k for k in df['KategorieTurnaje'].unique() if pd.notna(k)])
        vybrane_kategorie = st.sidebar.multiselect(
            "Filtrovat podle kategorie turnaje:",
            options=kategorie_turnaju,
            default=[k for k in kategorie_turnaju if k not in ["Bez kategorie", "Klubové a jiné podobné turnaje", "Funbridge"]]
        )
        
        all_participations_df = df
        if vybrane_kategorie:
            all_participations_df = all_participations_df[all_participations_df["KategorieTurnaje"].isin(vybrane_kategorie)]
        
        
        # Group by Legitimace only to sum days, then get person details from first row
        sportovci_dny = (
            all_participations_df
            .groupby("Legitimace")
            .agg(
                Pocet_dni=("DobaTurnaje", "sum"),
                Prijmeni=("Prijmeni", "first"),
                Jmena=("Jmena", "first"),
                Rocnik=("Rocnik", "first"),
                KlubNazev=("KlubNazev", "first"),
                Body=("Body", "first"),
                PoradiVZebricku=("PoradiVZebricku", "first"),
                Kategorie=("Kategorie", "first"),
                ClenPrispevek2025=("ClenPrispevek2025", "first"),
            )
            .reset_index()
        ).rename(columns={"Pocet_dni": "Pocet dni"})


        # Apply filters
        filtered_df = sportovci_dny[
            (sportovci_dny["Pocet dni"] >= min_dny) 
            & (sportovci_dny["Rocnik"] >= rok_od)
            & (sportovci_dny["Rocnik"] <= rok_do)
        ]
        
        if vybrane_kluby:
            filtered_df = filtered_df[filtered_df["KlubNazev"].isin(vybrane_kluby)]
        if only_with_prispevek:
            filtered_df = filtered_df[filtered_df["ClenPrispevek2025"] == "Ano"]




        # First create LegitimaceLink column
        display_df = filtered_df.copy()
        display_df["LegitimaceLink"] = display_df["Legitimace"].apply(
            lambda x: f"https://matrikacbs.cz/Detail-hrace.aspx?id={x}"
        )

        # Then remove unwanted columns
        display_df = display_df.drop(columns=["PoradiVZebricku"])

        # Split points into three columns
        display_df[["ZB", "SB", "KB"]] = pd.DataFrame(
            display_df["Body"].apply(split_points).tolist(), 
            columns=["ZB", "SB", "KB"],
            index=display_df.index
        )

        # Rename Body to BodyCelkem and move it to the end
        display_df = display_df.rename(columns={"Body": "BodyCelkem"})
        cols = [col for col in display_df.columns if col != "BodyCelkem"] + ["BodyCelkem"]
        display_df = display_df[cols]

        df_players = load_players(selected_season)
       
        players_count = len(df_players)
        st.metric("Celkový počet sportovců s členským příspěvkem",  players_count)
        st.download_button(
            label="Stáhnout seznam sportovců s členským příspěvkem",
            data=df_players.to_csv(index=False).encode("utf-8"),
            file_name="sportovci_s_clen_prispevek.csv",
            mime="text/csv",
        )

        # Display metrics
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Celkový počet sportovců", len(sportovci_dny))
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
                    display_text=".*id=(.*)",
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

        csv_all = sportovci_dny.to_csv(index=False).encode("utf-8")
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
        all_participations_df = all_participations_df[['Legitimace', 'Prijmeni', 'Jmena', 'Rocnik', 'KlubNazev', 'TurnajId', 'TurnajNazev', 'TurnajOd', 'TurnajDo', 'KategorieTurnaje', 'DobaTurnaje']
            ].sort_values(['Prijmeni', 'Jmena', 'TurnajOd'])
        
        # Display metrics
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Celkový počet účastí", len(df[df['Legitimace'].isin(sportovci_dny['Legitimace'])]))
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
    if debug:
        raise
