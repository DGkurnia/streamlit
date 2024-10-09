#Persiapan impor perpustakaan
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import streamlit as st
import plotly.express as px
import seaborn as sns
import warnings
warnings.filterwarnings('ignore')

#Persiapan kepala
st.set_page_config(page_title="Dashboard Kualitas Udara", layout="wide")
st.title('Dashboard Inspeksi Kualitas Udara')
st.write("Data Ini adalah hasil Inspeksi Kualitas udara Beijing.")
#Jalur relatif data
aotizpath = st.secrets["data_paths"]["aotizpath"]
changpath = st.secrets["data_paths"]["changpath"]
dingpath = st.secrets["data_paths"]["dingpath"]
dongpath = st.secrets["data_paths"]["dongpath"]
guapath = st.secrets["data_paths"]["guapath"]
gucpath = st.secrets["data_paths"]["gucpath"]
huapath = st.secrets["data_paths"]["huapath"]
nonpath = st.secrets["data_paths"]["nonpath"]
shunpath = st.secrets["data_paths"]["shunpath"]
tiapath = st.secrets["data_paths"]["tiapath"]
walpath = st.secrets["data_paths"]["walpath"]
waxpath = st.secrets["data_paths"]["waxpath"]
#Persiapan dataset (dari Aotizhongxin sampai Wanshouxigong untuk persembunyiaan)
aotizdf = pd.read_csv(os.getenv(aotizpath))
changdf = pd.read_csv(os.getenv(changpath))
dingdf = pd.read_csv(os.getenv(dingpath))
dongdf = pd.read_csv(os.getenv(dongpath))
guadf = pd.read_csv(os.getenv(guapath))
gucdf = pd.read_csv(os.getenv(gucpath))
huadf = pd.read_csv(os.getenv(huapath)) #Orang jepang atau cina menyebutnya 'huairou'
nonzhadf = pd.read_csv(os.getenv(nonpath))
shundf = pd.read_csv(os.getenv(shunpath))
tiadf =  pd.read_csv(os.getenv(tiapath))
waldf = pd.read_csv(os.getenv(walpath))
waxdf = pd.read_csv(os.getenv(waxpath))

#Persiapan penyatuan data (12 dataset ini adalah dataset kota Beijing)
beijingdf = pd.concat([aotizdf, changdf, dingdf, dongdf, guadf, gucdf, huadf, nonzhadf, shundf, tiadf, waldf, waxdf], ignore_index = True)

#Persiapan filtrasi stasiun
stasiun = beijingdf['station'].unique() #Penanda
pilihan = st.sidebar.selectbox("Pilih statiun Pengawasan", stasiun)
hasil = beijingdf[beijingdf['station'] == pilihan] #Filtrasi Stasiun

#Nilai Kunci
st.header(f"Air Quality Metrics for {hasil}") #Hasil Pilihan Stasiun
#Bagian Penampilan nilai metrik
metrik = {
    'Kadar PM2.5 (mikrometer/m^3)': hasil['PM2.5'].iloc[-1],
    'Kadar PM10 (mikrometer/m^3)': hasil['PM10'].iloc[-1],
    'Kadar Senyawa SO2 (mikrometer/m^3)': hasil['SO2'].iloc[-1],
    'Kadar Senyawa NO2 (mikrometer/m^3)': hasil['NO2'].iloc[-1],
    'Kadar Senyawa CO (mikrometer/m^3)': hasil['CO'].iloc[-1],
    'Kadar Senyawa oznon/(O3) (mikrometer/m^3)': hasil['O3'].iloc[-1],
    'Suhu (°C)': hasil['TEMP'].iloc[-1],
    'Tekanan (hPa)': hasil['PRES'].iloc[-1],
    'Nilai Kelembaban (°C)': hasil['DEWP'].iloc[-1],
    'Kadar Hujan (mm)': hasil['RAIN'].iloc[-1],
    'Kecepatan (m/s)': hasil['WSPM'].iloc[-1],
    'Arah angin': hasil['wd'].iloc[-1]
}
#itrasi nama untuk pilihan 
for namamet, nilaimet in metrik.items(): #variabel 'namamet' dan 'nilaimet'
    st.metric(label= namamet, value= nilaimet)
#--------------------------------------------------
#Inspeksi partikulat (nilai PM2.5 & nilai PM10)
[anPMa, dlPMa, anPMb, dlPMb] = [40, 150, 35, 75] 
#Batas aman
safety_limits = {
    'PM2.5 anual': anPMa, # Nilai Anual 
    'PM2.5 maksimal': dlPMa, # Batas Maksimal 2.5   
    'PM10 anual': anPMb,    
    'PM10 maksimal': dlPMb
}
#Keterangan (1. a adalah inepeksi PM2.5 b adalah PM10 2. kode an adalah anual kode ma adalah nilai maksimal)
#Grafik pengecekan partikulat
fig = px.line(hasil, x='datetime', y=['PM2.5', 'PM10'],
              labels={['PM2.5','PM10']: 'Kadar Partikulat', 'datetime': 'Tanggal'},
              title='Inspeksi Partikulat')
#Inspeksi Batas Aman
for pollutant, limit in safety_limits.items():
    fig.add_hline(y=limit, line_color="red", line_dash="dash",
                   annotation_text=f"{pollutant} Batas aman: {limit} µg/m³", 
                   annotation_position="top right")
#Ilustrasi normal untuk partikulat
st.plotly_chart(fig)
#Pemeriksaan batas partikulat
batasanu = hasil[(hasil['PM2.5'] > safety_limits['PM2.5 anual'] & hasil['PM2.5'] < safety_limits['PM2.5 maksimal']) 
                 | (hasil['PM10'] > safety_limits['PM10 anual'] & hasil['PM10'] < safety_limits['10 maksimal'])] #Batas anual
lwt = hasil[(hasil['PM2.5'] > safety_limits['PM2.5 maksimal']) | (hasil['PM10'] > safety_limits['PM10 maksimal'])] #Batas maksimal
#Area batas anual
if not lwt.empty:
    st.warning("Peringatan : Ini sudah terlalu bahaya")
elif not batasanu.empty and lwt.empty:
    st.warning("Peringatan : Ini harus hati-hati") #Kasus melewati batas anual (tapi di dibawah nilai maksimal)
else:
    st.success("Kadar udara masih aman")
 #------------------------------------------   
#Inspeksi batas senyawa karbon monoksida dan tiga senyawa lainnya
[cochl, cogl, ozmin, ozmax, nmax, smax ] = [4000, 30000, 50, 160, 200, 500]
#Deklarasi batas senyawa
colim = { 'China' : cochl, 'Global' : cogl} #Batas senyawa CO
ozlim = { 'minimum' : ozmin,'maksimum' : ozmax } #Ozon/ ozon
nitlim = {'anual': 40, 'maksimal' : nmax} # nitrogen dioksida (NO2)
sulplim = {'anual': 40, 'maksimal': smax} #Sulfur dioksida

#Pemeriksaan senyawa CO
#Grafik pengecekan senyawa karbon monoksida (CO)
fig = px.line(hasil, x='datetime', y=['CO'],
              labels={'CO': 'Konsentrasi CO', 'datetime': 'Tanggal'},
              title='Inspeksi Partikulat')
#Inspeksi Batas Aman
for pollutant, limit in colim.items():
    fig.add_hline(y=limit, line_color="red", line_dash="dash",
                   annotation_text=f"{pollutant} Batas aman: {limit} µg/m³", 
                   annotation_position="top right")
#Ilustrasi normal untuk senyawa (CO)
st.plotly_chart(fig)
#Pemeriksaan batas partikulat
lwtchina = hasil[(hasil['CO'] > colim['China']) & (hasil['CO'] < colim['Global'])] #Batas di 
lwtglobal = hasil[(hasil['CO'] > colim['Global'])] #Batas aglobal
#Area batas anual
if not lwtglobal.empty:
    st.warning("Peringatan : Ini sudah terlalu bahaya untuk global juga")
elif not lwtchina.empty and lwtglobal.empty:
    st.warning("Peringatan : Otoritas china boleh melarang ini") # 
else:
    st.success("Kadar senyawa CO masih aman")
#-----------------------------------------------
#Inspeksi senyawa Ozon (Grafik inspeksi O3)
#Grafik pengecekan senyawa Ozon (O3)
fig = px.line(hasil, x='datetime', y=['O3'],
              labels={'O3': 'Konsentrasi ozon', 'datetime': 'Tanggal'},
              title='Inspeksi Senyawa ozon')
#Inspeksi Batas Aman
for pollutant, limit in ozlim.items():
    fig.add_hline(y=limit, line_color="red", line_dash="dash",
                   annotation_text=f"{pollutant} Batas aman: {limit} µg/m³", 
                   annotation_position="top right")
#Ilustrasi normal untuk senyawa (CO)
st.plotly_chart(fig)
#Pemeriksaan kadar ozon
ozrdh = hasil[(hasil['O3'] < ozlim['minimum'])] #rendah
ozopti = hasil[(hasil['O3'] > ozlim['minimum']) & (hasil['O3'] < ozlim['maksimum'])] #optimal
ozmaks = hasil[(hasil['O3'] > ozlim['maksimum'])]
#Kondisional untuk senaywa ozon
if not ozmaks.empty :
    st.warning("Kadar ozon sangat tinggi")
elif (ozmaks.empy and ozrdh.empy) and not ozopti.empty:
    st.success("Kadar ozon masih aman")
else:
    st.warning("Kadar ozon sangat rendah")
#----------------------------------
#Inspeksi senyawa Nitrogen dioksida (Grafik inspeksi NO2)
#Grafik pengecekan senyawa Nitrogen Dioksida (NO2)
fig = px.line(hasil, x='datetime', y=['NO2'],
              labels={'NO2': 'Konsentrasi NO2', 'datetime': 'Tanggal'},
              title='Inspeksi Partikulat')
#Inspeksi Batas Aman
for pollutant, limit in nitlim.items():
    fig.add_hline(y=limit, line_color="red", line_dash="dash",
                   annotation_text=f"{pollutant} Batas aman: {limit} µg/m³", 
                   annotation_position="top right")
#Ilustrasi normal untuk senyawa (NO2)
st.plotly_chart(fig)
#Pemeriksaan kondisi NO2
nitinggi = hasil[(hasil['NO2'] < nitlim['maksimum']) & (hasil['NO2'] > nitlim['anual'])]
nibhy = hasil[(hasil['NO2'] > nitlim['maksimum'])]
#Kondisional senyawa NO2
if not nibhy.empty:
    st.warning("Kadar nitrogen dioksida terlalu berbahaya")
elif nibhy.empty and not nitinggi.empty:
    st.warning("Kadar nitrogen dioksida tinggo")
else :
    st.success("Kadar masih aman")
