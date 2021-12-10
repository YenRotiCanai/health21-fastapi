import pygsheets
import pandas as pd
import json
import googlemaps

#https://googlemaps.github.io/google-maps-services-python/docs/index.html
#https://pythonrepo.com/repo/nithinmurali-pygsheets-python-connecting-and-operating-databases

# google sheet 授權
gAuth = pygsheets.authorize(service_account_file='credentials.json')

# google map api 授權
gmaps = googlemaps.Client(key='AIzaSyBR2TL-7XibVRMbpjzkVDyLJzFQ390mAes')

# 地址轉經緯度
def geocoding(addr):
    # Geocoding an address #會拿到一個list，但我們要dict才比較好撈經緯度，所以要把他變成dict
    geocode_result = gmaps.geocode(addr) 

    #先把他轉成 json，變成一個string
    j = json.dumps(geocode_result)

    #去頭去尾，再 loads 回來就會變成 dict
    j1 = j[1:-1]
    j2 = json.loads(j1)

    #最後就可以把經緯度撈出來了
    lat = j2['geometry']['location']['lat']
    lng = j2['geometry']['location']['lng']

    return [lat,lng]

# 算距離
def calc_dist(origin, destination):
    # 呼叫 distance matrix API
    distance_result = gmaps.distance_matrix(origin, destination)

    # 把距離撈出來
    text = distance_result['rows'][0]['elements'][0]['distance']['text']

    # 字串處理，只拿前面的數字，不要後面的 km
    # 這裡會有個問題：如果他距離小於1公里，還是會當成1公里，但因為運費是以公里數計算，所以不到1公里也算1公里，超過的話就算2公里，以此類推
    # 如果要算更細一點，可以改成取 value 而不是 text
    text_split = text.split(" ")
    dist = text_split[0]

    print("calc_dis done")
    return dist

def main_sheet2df(sheetUrl):
    sheet = gAuth.open_by_url(sheetUrl)

    # 選第一個工作列表
    wks = sheet[0]

    # 把工作表轉成 dataframe
    cont_data = wks.get_all_values(include_tailing_empty=False, include_tailing_empty_rows=False)
    cont_df = pd.DataFrame(cont_data, columns = cont_data[0]) # 直接用他的第一行來當做 title
    cont_df = cont_df.drop(cont_df.index[0])

    # 篩選出要外送的人
    cont_df2 = cont_df[(cont_df['取餐方式'] == "外送") | (cont_df['取餐方式'] == "餐廳")]
    cont_df2.reset_index(drop=True, inplace=True)
    
    # 把經緯度和距離整合到新的 df，然後存到新的工作表
    dist_list = []
    lat_list = []
    lng_list = []

    for i in range(len(cont_df2)):
        origin = cont_df2['餐廳地址'][i]
        destination = cont_df2['取餐地點'][i]

        latlng = geocoding(destination)
        lat_list.append(latlng[0])
        lng_list.append(latlng[1])

        dist = calc_dist(origin, destination)
        dist_list.append(dist)

    cont_df3 = cont_df2.assign(lat=lat_list, lng=lng_list, 距離km=dist_list)

    sheet.add_worksheet('外送名單')
    wksdeliverList = sheet.worksheet_by_title('外送名單')
    wksdeliverList.set_dataframe(cont_df3,(1,1))

    print("main_sheet2df done")

    return cont_df3

# 把路線變成 dataframe 存到新的工作表
def route2df(df, routes, sheetUrl):
    sheet = gAuth.open_by_url(sheetUrl)

    r_df = pd.DataFrame(columns=['路線編號','送餐順序'])
  
    for i in range(len(routes)):
        r_df.loc[i] = [i+1, routes[i]]

    sheet.add_worksheet('路線順序')
    wksRoutes = sheet.worksheet_by_title('路線順序')
    wksRoutes.set_dataframe(r_df,(1,1))

    deliverList_df = pd.DataFrame()
    for i in range(len(routes)):
        for j in range(len(routes[i])):
            order = routes[i][j]
            deliverList_df = deliverList_df.append(df.loc[order])

    deliverList_df.reset_index(inplace=True)
    deliverList_df.rename(columns={'index':'順序編號'}, inplace=True)

    sheet.add_worksheet('送餐順序名單')
    wksRoutesList = sheet.worksheet_by_title('送餐順序名單')
    wksRoutesList.set_dataframe(deliverList_df, (1,1))

    print("route2df done")

def routeListSheet2json(sheetUrl):
    sheet = gAuth.open_by_url(sheetUrl)

    wksDeliverList = sheet.worksheet_by_title('送餐順序名單')
    deliverList_json = wksDeliverList.get_as_df().to_json(orient='index', force_ascii=False)

    print("routeListSheet2json done")

    return deliverList_json