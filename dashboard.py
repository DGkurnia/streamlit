#Persiapan impor perpustakaan
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import streamlit as st
import plotly.express as px
import datetime


#Persiapan dataset (dari Aotizhongxin sampai Wanshouxigong)
aotizdf = pd.read_csv('aqinsc/aotizhongxin-c.csv')
changdf = pd.read_csv('aqinsc/changping-c.csv')
dingdf = pd.read_csv('aqinsc/dingling-c.csv')
dongdf = pd.read_csv('aqinsc/dongsi-c.csv')
guadf = pd.read_csv('aqinsc/guanyuan-c.csv')
gucdf = pd.read_csv('aqinsc/gucheng-c.csv')
huadf = pd.read_csv('aqinsc/huairo-c.csv')
nonzhadf = pd.read_csv('aqinsc/nonzhanguan-c.csv')
shundf = pd.read_csv('aqinsc/shunyi-c.csv')
tiadf =  pd.read_csv('aqinsc/tiantan-c.csv')
waldf = pd.read_csv('aqinsc/wanliu-c.csv')
waxdf = pd.read_csv('aqinsc/wanshouxigong-c.csv')


#Persiapan penyatuan data (12 dataset ini adalah dataset kota Beijing)
beijingdf = pd.concat([aotizdf, changdf, dingdf, dongdf, guadf, gucdf, huadf, nonzhadf, shundf, tiadf, waldf, waxdf], index = False)


#Persiapan kepala
st.title('Dashboard Inspeksi Kualitas Udara')
st.set_page_config(page_title="Dashboard Kualitas Udara", layout="wide")
st.write("Data Ini adalah hasil Inspeksi Kualitas udara Beijing.")

#Persiapan filtrasi stasiun
stasiun = beijingdf['station'].unique() #Penanda
pilihan = st.sidebar.selectbox("Select Monitoring Station", stasiun)
hasil = beijingdf[beijingdf['station'] == pilihan] #Filtrasi Stasiun

#Nilai Kunci
st.header(f"Air Quality Metrics for {hasil}") #Hasil Pilihan Stasiun
#Bagian Penampilan nilai metrik
metrik = {
    'Kadar PM2.5': hasil['PM2.5'].iloc[-1],
    'Kadar PM10': hasil['PM10'].iloc[-1],
    'Kadar Senyawa SO2': hasil['SO2'].iloc[-1],
    'Kadar Senyawa NO2': hasil['NO2'].iloc[-1],
    'Kadar Senyawa CO': hasil['CO'].iloc[-1],
    'Kadar Senyawa oznon (O3)': hasil['O3'].iloc[-1],
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
fig = px.line(hasil, x='peta waktu', y=['PM2.5', 'PM10'],
              labels={'Nilai': 'Concentration', 'peta waktu': 'Tanggal'},
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
fig = px.line(hasil, x='peta waktu', y=['CO'],
              labels={'Nilai': 'Konsentrasi CO', 'peta waktu': 'Tanggal'},
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
fig = px.line(hasil, x='peta waktu', y=['O3'],
              labels={'Nilai': 'Konsentrasi ozon', 'peta waktu': 'Tanggal'},
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
fig = px.line(hasil, x='peta waktu', y=['NO2'],
              labels={'Nilai': 'Konsentrasi NO2', 'peta waktu': 'Tanggal'},
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