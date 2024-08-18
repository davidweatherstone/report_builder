from datetime import date

import pandas as pd


_2_years_ago = date.today().replace(year=date.today().year-2).replace(day=1).strftime("%Y%m%d")
_2_years_ahead = date.today().replace(year=date.today().year+2).replace(day=1).strftime("%Y%m%d")

year_2_years_ago = date.today().replace(year=date.today().year-2).year
year_10_years_ago = date.today().replace(year=date.today().year-10).year


sources = pd.read_excel(r"./Data/Sources.xlsx", usecols=["Visual", "Index", "Units", "Raw Unit", "Source Link"])

eurostat_data_dictionary = r"./Data/Eurostat Data Dictionary.xlsx"

geography = pd.read_excel(eurostat_data_dictionary, sheet_name="geography")
labour_obs = pd.read_excel(eurostat_data_dictionary, sheet_name="labour_obs_value")
labour_unit = pd.read_excel(eurostat_data_dictionary, sheet_name="labour_unit")
nace_r2 = pd.read_excel(eurostat_data_dictionary, sheet_name="nace_r2").drop_duplicates(subset="NACE_R2 code", keep="last")

general = pd.read_excel(r"./Data/Cost_Drivers_Data.xlsx", sheet_name="Monthly")
eu_inflation = pd.read_csv(r"./Data/ei_cphi_m_linear.csv", usecols=["unit", "indic", "geo", "TIME_PERIOD", "OBS_VALUE"])
eu_labour = pd.read_csv(r"./Data/ei_lmlc_q_linear.csv", usecols=["TIME_PERIOD", "geo", "unit", "indic", "s_adj", "OBS_VALUE", "nace_r2"])
eu_transport = pd.read_csv(r"./Data/teicp070_linear.csv")
eu_agriculture = pd.read_csv(r"./Data/apro_cpsh1_linear.csv")

locations = ["Germany", "Netherlands", "France", "Italy", "Ireland", "Poland", "Belgium", "European Union 27 countries (from 2020)"]
industries = ["Business economy", "Mining and quarrying", "Manufacturing", 
              "Industry (except construction)", "Construction", "Transport & storage", "Health"]


eu_inflation_tweaked = (eu_inflation
 .assign(
     Date=lambda df_: pd.to_datetime(df_["TIME_PERIOD"] + "-01", format="%Y-%m-%d"),
     Index="Inflation"
    )
 .merge(geography, left_on="geo", right_on="Geo Short", how="left", validate="m:1")
 .merge(sources, left_on="Index", right_on="Index", how="left")
 .query("unit == 'HICP2015' &" \
        "indic == 'CP-HI00' &" \
        "`Geo Long`.isin(@locations)"
        )
 .drop(columns="Index")
 .rename(columns={"OBS_VALUE": "Value", "Geo Long": "Index"})
 .replace("European Union 27 countries (from 2020)", "EU 27 countries")
)

eu_inflation_tweaked_filtered = eu_inflation_tweaked.query("Date >= @_2_years_ago")


eu_inflation_yoy_tweaked = (eu_inflation_tweaked
 .assign(Prev_Date=lambda df_: df_["Date"] - pd.DateOffset(years=1),
         Visual="Inflation, Year-on-Year Rate (%)")
 .merge(eu_inflation_tweaked, left_on=["Prev_Date", "Index"], right_on=["Date", "Index"], how="left")
 .assign(Value_YOY=lambda df_: ((df_["Value_x"] - df_["Value_y"])/ df_["Value_y"]) * 100)
 .rename(columns=lambda df_: df_.replace("_x", ""))
 .drop(columns=["Value", "Units"]).rename(columns={"Value_YOY": "Value"})
 .query("Date >= @_2_years_ago")
 .replace("European Union 27 countries (from 2020)", "EU 27 countries")
)


labour_by_country_tweaked = (eu_labour
 .assign(Year=lambda df_: df_["TIME_PERIOD"].str[:4].astype("uint16"))
 .merge(geography, left_on="geo", right_on="Geo Short", how="left", validate="m:1")
 .query(
      "unit == 'I20' &" \
      "indic == 'LM-LCI-TOT' & " \
      "Year >= @year_2_years_ago & " \
      "`Geo Long`.isin(@locations) & " \
      "s_adj == 'SCA'"  
          )
 .assign(Date=lambda df_: pd.to_datetime(
                                    df_["Year"].astype("str") + 
                                    (df_["TIME_PERIOD"].str[-1].astype("uint8") * 3).astype("str") + 
                                    "01", format="%Y%m%d")
 )
 .groupby(["Geo Long", "Date"], as_index=False).agg(Value=("OBS_VALUE", "mean"))
 .assign(Index="Labour Cost", Visual="Labour Cost by Country")
 .merge(sources.loc[:,["Index", "Units", "Source Link"]], left_on="Index", right_on="Index", how="left")
 .drop(columns="Index")
 .rename(columns={"Geo Long": "Index"})
)


labour_by_industry_tweaked = (eu_labour
 .assign(Year=lambda df_: df_["TIME_PERIOD"].str[:4].astype("uint16"))
 .merge(nace_r2, left_on="nace_r2", right_on="NACE_R2 code", how="left", validate="m:1")
 .query(
     "unit == 'I20' &" \
     "indic == 'LM-LCI-TOT' & " \
     "Year >= @year_2_years_ago & " \
     "s_adj == 'SCA' &" \
     "`Short meaning`.isin(@industries)"  
         )
 .assign(Date=lambda df_: pd.to_datetime(
                                    df_["Year"].astype("str") + 
                                    (df_["TIME_PERIOD"].str[-1].astype("uint8") * 3).astype("str") + 
                                    "01", format="%Y%m%d")
 )
 .groupby(["Short meaning", "Date"], as_index=False).agg(Value=("OBS_VALUE", "mean"))
 .assign(Index="Labour Cost", Visual="Labour Cost by Industry")
 .merge(sources.loc[:,["Index", "Units", "Source Link"]], left_on="Index", right_on="Index", how="left")
 .drop(columns="Index")
 .rename(columns={"Short meaning": "Index"})
)


transport_tweaked = (eu_transport
 .merge(geography, left_on="geo", right_on="Geo Short", how="left", validate="m:1")
 .assign(
     Date=lambda df_: pd.to_datetime(df_["TIME_PERIOD"] + "-01", format="%Y-%m-%d"),
     Index="HICP Transport"
    )
 .query(
   "unit == 'I15' &" \
   "`Geo Long`.isin(@locations)"
  )
  .merge(sources, left_on="Index", right_on="Index", how="left")
  .drop(columns="Index")
  .rename(columns={"OBS_VALUE": "Value", "Geo Long": "Index"})
  .replace("European Union 27 countries (from 2020)", "EU 27 countries")
 )

fuel_tweaked = (general
 .assign(Date=lambda df_: pd.to_datetime(df_["Month"]))
 .query("Date >= @_2_years_ago")
 .melt(id_vars=["Date"], 
       value_vars=list(general.columns[1:]),
       var_name="Index", value_name="Value")
 .query("~Value.isna()")
 .merge(sources, left_on="Index", right_on="Index", how="left")
 .query("Visual == 'Fuel'")
)

fuel_tweaked_crude = fuel_tweaked.query("Index == 'Crude Oil'")
fuel_tweaked_not_crude = fuel_tweaked.query("Index != 'Crude Oil'")


food_oils = (general
 .assign(Date=lambda df_: pd.to_datetime(df_["Month"]))
 .query("Date >= @_2_years_ago")
 .melt(id_vars=["Date"], 
       value_vars=list(general.columns[1:]),
       var_name="Index", value_name="Value")
 .query("~Value.isna()")
 .merge(sources, left_on="Index", right_on="Index", how="left")
 .query("Visual == 'Food Oils'")
)


top_10_producers_C0000 = list((eu_agriculture
 .query(
   "geo != 'UK' &" \
   "crops == 'C0000' &" \
   "strucpro == 'AR' &" \
   "~geo.str.contains('EU') &" \
   "~geo.str.contains('EE') &" \
   "TIME_PERIOD >= @year_10_years_ago")
 .groupby(["geo"], as_index=False).agg(Value=("OBS_VALUE", "sum"))
 .sort_values("Value", ascending=False)
 .head(10).geo
))

agriculture_cereals = (eu_agriculture
 .query(
   "geo.isin(@top_10_producers_C0000) &" \
   "crops == 'C0000' &" \
   "strucpro == 'AR' &" \
   "TIME_PERIOD >= @year_10_years_ago")
 .merge(geography, left_on="geo", right_on="Geo Short", how="left", validate="m:1")
 .loc[:,["TIME_PERIOD", "OBS_VALUE", "Geo Long"]]
 .assign(Index="Agriculture, Cereals")
 .merge(sources, left_on="Index", right_on="Index", how="left")
 .drop(columns="Index")
 .rename(columns={"TIME_PERIOD": "Date", "OBS_VALUE": "Value", "Geo Long": "Index"})
)

top_10_producers_P0000 = list((eu_agriculture
 .query(
   "geo != 'UK' &" \
   "crops == 'P0000' &" \
   "strucpro == 'AR' &" \
   "~geo.str.contains('EU') &" \
   "~geo.str.contains('EE') &" \
   "TIME_PERIOD >= @year_10_years_ago")
 .groupby(["geo"], as_index=False).agg(Value=("OBS_VALUE", "sum"))
 .sort_values("Value", ascending=False)
 .head(10).geo
))

agriculture_dry_pulses = (eu_agriculture
 .query(
   "geo.isin(@top_10_producers_P0000) &" \
   "crops == 'P0000' &" \
   "strucpro == 'AR' &" \
   "TIME_PERIOD >= @year_10_years_ago")
 .merge(geography, left_on="geo", right_on="Geo Short", how="left", validate="m:1")
 .loc[:,["TIME_PERIOD", "OBS_VALUE", "Geo Long"]]
 .assign(Index="Agriculture, Dry Pulses")
 .merge(sources, left_on="Index", right_on="Index", how="left")
 .drop(columns="Index")
 .rename(columns={"TIME_PERIOD": "Date", "OBS_VALUE": "Value", "Geo Long": "Index"})
)

top_10_producers_V0000 = list((eu_agriculture
 .query(
   "geo != 'UK' &" \
   "crops == 'V0000' &" \
   "strucpro == 'AR' &" \
   "~geo.str.contains('EU') &" \
   "~geo.str.contains('EE') &" \
   "TIME_PERIOD >= @year_10_years_ago")
 .groupby(["geo"], as_index=False).agg(Value=("OBS_VALUE", "sum"))
 .sort_values("Value", ascending=False)
 .head(10).geo
))

agriculture_vegetables = (eu_agriculture
 .query(
   "geo.isin(@top_10_producers_V0000) &" \
   "crops == 'V0000' &" \
   "strucpro == 'AR' &" \
   "TIME_PERIOD >= @year_10_years_ago")
 .merge(geography, left_on="geo", right_on="Geo Short", how="left", validate="m:1")
 .loc[:,["TIME_PERIOD", "OBS_VALUE", "Geo Long"]]
 .assign(Index="Agriculture, Vegetables")
 .merge(sources, left_on="Index", right_on="Index", how="left")
 .drop(columns="Index")
 .rename(columns={"TIME_PERIOD": "Date", "OBS_VALUE": "Value", "Geo Long": "Index"})
 .replace(8484.0, 848.0)
)