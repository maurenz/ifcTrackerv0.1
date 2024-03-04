import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

# Streamlit UI
st.title("Ifc Tracker")

# Datei-Upload-Widget
uploaded_file = st.file_uploader("Wähle eine Excel-Datei aus", type=['xlsx'])

if uploaded_file is not None:
    # Lese die Excel-Datei in ein Pandas DataFrame
    df = pd.read_excel(uploaded_file)

    # Datumsformat konvertieren
    df['Datum'] = pd.to_datetime(df['Datum'], format='%d.%m.%Y')
    


    # Multiple choice Selektoren
    default_cluster = ["HAA"] if "HAA" in df['Cluster'].unique() else None
    default_values_tps = [value for value in [1, 2, 3] if value in df['TP'].unique()]

    selected_clusters = st.multiselect('Wähle Cluster:', options=df['Cluster'].unique(), default=default_cluster)
    selected_tps = st.multiselect('Wähle TP:', options=df['TP'].unique(), default=[1, 2, 3])
    
    # Daten basierend auf Auswahl filtern
    filtered_data = df[df['Cluster'].isin(selected_clusters) & df['TP'].isin(selected_tps)]
    
    if not filtered_data.empty:
        # Visualisierung
        fig, ax = plt.subplots()
        for (cluster, tp), group in filtered_data.groupby(['Cluster', 'TP']):
            ax.plot(group['Datum'], group['percentage'], label=f' {cluster}, TP {tp}')
            # Zeichne Kreise an jedem Datenpunkt
            ax.scatter(group['Datum'], group['percentage'], s=10)
    
        # Setze die x-Ticks auf die eindeutigen Datumsangaben in den gefilterten Daten
        ax.set_xticks(filtered_data['Datum'].unique())
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%d.%m.%y'))
        ax.set_xlabel('Datum')
        ax.set_ylabel('Developement [%]')
        ax.legend()
        plt.xticks(rotation=45)  # Dreht die x-Achsen-Beschriftungen für bessere Lesbarkeit
    
        # Zeichne graue horizontale Linien bei jedem Y-Achsen-Label
        y_ticks = ax.get_yticks()
        for y in y_ticks:
            ax.axhline(y, color='#cccccc', linestyle='-', linewidth=0.3)
    
        st.pyplot(fig)
    else:
        st.write("Bitte wähle mindestens einen Cluster und einen TP aus, um die Daten anzuzeigen.")
    
    
    #df.sort_values('Datum', inplace=True)
    
    # Berechnen der Differenz "Change"
    def calculate_percentage_change(group):
        if len(group) > 1:
            return group['percentage'].iloc[-1] - group['percentage'].iloc[0]
        else:
            return 0  # Keine Veränderung, wenn nur ein Datum vorhanden ist
    
    # Gruppieren nach "Cluster" und "TP", und Anwenden der Berechnung
    change_df = df.groupby(['Cluster', 'TP']).apply(calculate_percentage_change).reset_index(name='Change 1. - last [%]')
    
    # Extrahiere den Wert von "IfcElemente" des aktuellsten Datums jeder Gruppe
    ifc_elements_latest = df.groupby(['Cluster', 'TP']).apply(lambda x: x.loc[x['Datum'].idxmax(), 'IfcElemente']).reset_index(name='currentIfcElements')
    
    # Füge die neue Spalte "IfcElements" zu "change_df" hinzu
    change_df = pd.merge(change_df, ifc_elements_latest, on=['Cluster', 'TP'])
    
    # Prozentzeichen zu den Werten in "Change 1. - last [%]" hinzufügen
    change_df['Change 1. - last [%]'] = change_df['Change 1. - last [%]']
    
    # Tabelle nach "Change 1. - last [%]" aufsteigend sortieren
    change_df.sort_values('Change 1. - last [%]', inplace=True)
    change_df.reset_index(drop=True, inplace=True)
    # Aktualisierte Tabelle anzeigen
    st.table(change_df)
