import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta
import os

folder_name = 'data'
if not os.path.exists(folder_name):
    os.makedirs(folder_name)

print(f"Folder roboczy to: {os.getcwd()}")
print(f"Dane trafią do folderu: {os.path.abspath(folder_name)}")

print("Generowanie danych rozpoczęte...")

np.random.seed(42)
num_customers = 100
start_date = datetime(2025, 1, 1)
end_date = datetime(2025, 12, 31)
date_range = pd.date_range(start=start_date, end=end_date, freq='h') 

# Taryfy
tariffs_data = {
    'ID_Taryfy': ['G11', 'G12'],
    'Nazwa': ['Taryfa Uniwersalna', 'Taryfa Dzień/Noc'],
    'Stawka_Szczyt': [0.75, 0.98],       # G12 droższa w dzień
    'Stawka_PozaSzczytem': [0.75, 0.45]  # G12 tańsza w nocy
}
df_tariffs = pd.DataFrame(tariffs_data)

# Klienci
cities = ['Gdańsk', 'Gdynia', 'Sopot', 'Słupsk', 'Elbląg']
df_customers = pd.DataFrame({
    'ID_Klienta': range(1001, 1001 + num_customers),
    'Miasto': np.random.choice(cities, num_customers),
    'Typ_Licznika': np.random.choice(['Smart', 'Standard'], num_customers, p=[0.8, 0.2]),
    'ID_Taryfy': np.random.choice(['G11', 'G12'], num_customers, p=[0.6, 0.4])
})

# Fakt: odczyty
total_rows = len(df_customers) * len(date_range)
print(f"Generowanie {total_rows} wierszy danych transakcyjnych...")

df_customers['key'] = 1
df_dates = pd.DataFrame({'Data_Godzina': date_range})
df_dates['key'] = 1
df_dates['Godzina'] = df_dates['Data_Godzina'].dt.hour
df_dates['Miesiac'] = df_dates['Data_Godzina'].dt.month

# Łączenie (Cross Join)
df_facts = pd.merge(df_customers, df_dates, on='key').drop('key', axis=1)

# Logika biznesowa
random_factors = np.random.uniform(0.5, 1.5, size=len(df_facts))

conditions = [
    (df_facts['Godzina'].between(6, 9)) | (df_facts['Godzina'].between(17, 22)), # Szczyt
    (df_facts['Godzina'].between(1, 5)) # Noc (małe zużycie)
]
choices = [1.8, 0.3] # Mnożniki
time_factor = np.select(conditions, choices, default=1.0)

# Profil sezonowy (Zima = więcej prądu)
season_factor = np.where(df_facts['Miesiac'].isin([11, 12, 1, 2]), 1.4, 0.9)

# Finalne kWh
df_facts['Zuzycie_kWh'] = (random_factors * time_factor * season_factor).round(3)

# Oczyszczanie tabeli faktów (zostawiamy tylko klucze obce i metryki)
df_facts_final = df_facts[['Data_Godzina', 'ID_Klienta', 'Zuzycie_kWh']]

# Używamy os.path.join dla pewności
df_tariffs.to_csv(os.path.join(folder_name, 'DimTaryfa.csv'), index=False)
df_customers.drop('key', axis=1).to_csv(os.path.join(folder_name, 'DimKlient.csv'), index=False)
df_facts_final.to_csv(os.path.join(folder_name, 'FactOdczyty.csv'), index=False)

print(f"Pliki zapisane w: {os.path.abspath(folder_name)}")
