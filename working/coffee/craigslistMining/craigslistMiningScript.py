from selenium import webdriver
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import pandas as pd
import geopandas as gpd

neigh = gpd.read_file('../data/chicago/v2 07012017/ChicagoNeighborhoods.shp')



home = 'https://chicago.craigslist.org/search/apa'
base = 'https://chicago.craigslist.org'

storage = {
    'ids':[],
    'price':[],
    'longitude':[],
    'latitude':[],
    'neighborhood':[]
}

if __name__=='__main__':
    driver = webdriver.Chrome('./chromedriver')
    for neigh in [i for i in neigh.pri_neigh]:
        driver.get(home)
        search = driver.find_element_by_id('query')

        search.clear()
        search.send_keys(neigh)
        search.submit()

        try:
            viewButton = driver.find_element_by_id('gridview')
            viewButton.click()

            changeView = driver.find_element_by_id('listview')
            changeView.click()
        except:
            pass

        html = driver.page_source
        soup = BeautifulSoup(html,"lxml")
        s = soup.find_all(attrs={'class':'result-title hdrlnk'})
        links = [i['href'] for i in s]
        ids = [i['data-id'] for i in s]

        for i in range(len(links)):
            try:
                driver.get(base + links[i])
                price = driver.find_element_by_class_name('price')
                geo = driver.find_element_by_id('map')

                storage['price'].append(price.text)
                storage['longitude'].append(geo.get_attribute('data-longitude'))
                storage['latitude'].append(geo.get_attribute('data-latitude'))
                storage['ids'].append(ids[i])
                storage['neighborhood'].append(neigh)
            except:
                next

    driver.close()

    df = pd.DataFrame(storage)
    print(df.shape)
    df.to_csv('neighborhoodRent_081817.csv',index=False)
