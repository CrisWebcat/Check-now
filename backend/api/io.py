import xarray as xr

def read_netcdf_timeseries(path, varname, lat, lon):
    ds = xr.open_dataset(path)
    # Seleccionar punto más cercano
    sel = ds[varname].sel(lat=lat, lon=lon, method="nearest")
    # Convertir a pandas Series
    sr = sel.to_series()
    return sr.reset_index().rename(columns={0: varname})
