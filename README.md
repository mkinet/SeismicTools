# SeismicTools
Python Libraries for Seismic Tools used in TE

## Introduction 
The present repo contains a set of python libraries
developped to facilitate the use of old fashioned tools within TE. 

The main File 'Seismictools.py' defines classes to manipulate:
- seismic response spectra
- time histories

The methods defined in the classes permit the definition of these
objects through xls or csv file, plotting them and save the figure,
perform average or enveloppe, convert between different format, etc.

Furthermore, the files PrePostShake.py and prepostTHGE.py can be used 
as a pre/post-processor for the following tools :

- SHAKE (Site analysis study for GMRS calculations)
- THGE (time-history generation from a response spectra) 

These two libraries rely on the SeismicTools library which is more 
general.

Further development of the libraries should include the following
capabilities: 

- conversion of response spectra to time-histories using either the 
  program GASPEC or a refreshed version of it.
- CAV factor computation of a given spectra or TH
- Arrhias integral calculation
- correlation calculation between two time-histories
- improve methods to make average and enveloppe (so that they don't 
  need to be defined at the same points).
