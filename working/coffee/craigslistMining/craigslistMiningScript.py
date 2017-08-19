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
    'neighborhood':[],
    'specs':[]
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
                try:
                    specs = driver.find_element_by_xpath('(//div[@class="mapAndAttrs"]\
                                         /p[@class="attrgroup"]/span[@class="shared-line-bubble"])[1]')
                    specs = specs.text
                except:
                    specs = ""

                storage['price'].append(price.text)
                storage['longitude'].append(geo.get_attribute('data-longitude'))
                storage['latitude'].append(geo.get_attribute('data-latitude'))
                storage['ids'].append(ids[i])
                storage['neighborhood'].append(neigh)
                storage['specs'].append(specs)
            except:
                next

    driver.close()

    df = pd.DataFrame(storage)
    print(df.shape)
    # save raw data
    df.to_csv('neighborhoodRent_081817.csv',index=False)

    # process raw data
    df = df.drop_duplicates('ids')
    df.price  = df.price.str[1:].astype(float)

    # extract bedroom and bathrooms from the BR/BA button element
    df[['bedroom','bathroom']] = df.specs.str.split(' / ',expand=True)
    df.bedroom = df.bedroom.str.extract(r'(\d+[\d.]{,1})').astype(float)
    df.bathroom = df.bathroom.str.extract(r'(\d+[\d.]{,1})').astype(float)

    # fill missing ones with the mean value
    df.bedroom = df.bedroom.fillna(df.bedroom.mean()).astype(float)
    df.bathroom = df.bathroom.fillna(df.bathroom.mean()).astype(float)

    # remove outliers, some spec scraping extracted square feet
    df = df[df.bedroom <= 10]

    # save processed version of rent data
    df.to_csv('neighborhoodRent_processed081817.csv',index=False)
