import scrapy
from scrapy import Selector
from selenium import webdriver
import json
import time


class SaleListingsSpiderSpider(scrapy.Spider):
    name = 'sale_listings_spider'
    allowed_domains = ['zingat.com']
    #start_urls = ['http://zingat.com/en/for-sale-apartment']
    page_number = 2

    def start_requests(self):
        url = "http://zingat.com/en/for-sale-apartment"
        yield scrapy.Request(url=url, callback=self.parse_listings_pages)

    def parse_listings_pages(self, response):
        listings = response.xpath('//a[@class="zl-card-inner"]/@href').getall()
        #listings = response.xpath('//a[@class="zl-card-inner"]/@href').get()

        for listing in listings:
            time.sleep(15)
            yield response.follow(url=listing, callback=self.parse_listings)
            time.sleep(15)

        next_page = 'https://www.zingat.com/en/for-sale-apartment?page=' + str(SaleListingsSpiderSpider.page_number)
        if SaleListingsSpiderSpider.page_number < 50:
            time.sleep(50)
            SaleListingsSpiderSpider.page_number += 1
            yield response.follow(url=next_page, callback=self.parse_listings_pages)
            time.sleep(10)

    def parse_listings(self, response):
        try:
            options = webdriver.ChromeOptions()
            options.add_argument("headless")
            #options.add_argument("--remote-debugging-port=9222")
            options.add_experimental_option('excludeSwitches', ['enable-logging'])
            desired_capabilities = options.to_capabilities()
            driver = webdriver.Chrome(desired_capabilities=desired_capabilities, options = options)

            current_url = response.url
            #current_url = 'http://zingat.com//en/didim-akbuk-de-mustakil-girisli-havuzlu-3-1-daire-4032010i'
            #print(current_url)
            driver.get(current_url)
            time.sleep(3)
            #driver.implicitly_wait(5)

            try:

                title1 = response.xpath('//h1[@data-zingalite="listing-detail-title"]/text()').get()
                title2 = response.xpath('//label[@id="seo_ProductTitle"]/text()').get()
                price = response.xpath('//label[@id="seo_ProductPriceAmount"]/text()').get()
                currency = response.xpath('//label[@id="seo_ProductPriceCurrency"]/text()').get()
                sale_or_rent = response.xpath('//label[@id="seo_ProductType"]/text()').get()
                size_of_appartment = response.xpath('//label[@id="seo_ProductSize"]/text()').get()
                number_of_rooms = response.xpath('//label[@id="seo_ProductRoomSlug"]/text()').get()
                #detail_labels = response.xpath('//div[@class="detail-info not-printable"]/div/span/text()').getall()
                detail_text_list = response.xpath('//div[@class="detail-info not-printable"]/div/strong/text()').getall()
                month_list = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
                for month in month_list:
                    for detail_text in detail_text_list:
                        if month in detail_text:
                            date_published = detail_text

                time.sleep(2)
                features_list = driver.find_element_by_class_name("attribute-detail-list")
                features_list_names = features_list.find_elements_by_xpath("//li[@class='col-md-6']/strong")
                features_list_data = features_list.find_elements_by_xpath("//li[@class='col-md-6']/span")
                feature_dict = {}

                for feature_name, feature_data in zip(features_list_names, features_list_data):
                    feature_dict[feature_name.text] = feature_data.text

                time.sleep(2)
                description = response.xpath('//div[@class="detail-text-desktop"]/p/text()').get()
                passive_other_features = driver.find_elements_by_xpath("//div[@class='col-md-3 attr-item passive']")
                active_other_features = driver.find_elements_by_xpath("//div[@class='col-md-3 attr-item']")

                other_features_dict = {}

                for feature in passive_other_features:
                    if feature.text != "":
                        other_features_dict[feature.text] = 0

                for feature in active_other_features:
                    if feature.text != "":
                        string_form = feature.text
                        string_form = string_form.removesuffix(': Yes')
                        other_features_dict[string_form] = 1

                time.sleep(2)
                realtor_company_name = driver.find_elements_by_class_name("agent-company-link")

                agency_name = None
                for i in realtor_company_name:
                    agency_name = realtor_company_name[1].text


                feature_dict = str(feature_dict)
                other_features_dict = str(other_features_dict)
                agency_name = str(agency_name)
                date_published = str(date_published)

                time.sleep(2)

                yield {
                    'title': title1,
                    'title2': title2,
                    'price': price,
                    'currency': currency,
                    'sale or rent' : sale_or_rent,
                    'size of appartment': size_of_appartment,
                    'number of rooms': number_of_rooms,
                    'features': feature_dict,
                    'other features': other_features_dict,
                    'realtor company name': agency_name,
                    'date published': date_published,
                }

                time.sleep(2)
                driver.quit()
                time.sleep(2)
            except:
                time.sleep(2)
                driver.quit()
                time.sleep(2)

        except:
            driver.quit()
            pass