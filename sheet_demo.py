import pygsheets

gc = pygsheets.authorize(service_account_file='credentials.json')
g = gc.open_by_key('1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms')
