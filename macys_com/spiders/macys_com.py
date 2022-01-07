# -*- coding: utf-8 -*-
import scrapy
from scrapy.exceptions import CloseSpider
from scrapy import Request
from urlparse import urlparse
from json import loads
from datetime import date
# import json
import re

class macys_comSpider(scrapy.Spider):

    name = "macys_com_spider"

    use_selenium = False

    next_count = 1

    nextCountJson = {}
###########################################################

    def __init__(self, *args, **kwargs):
        super(macys_comSpider, self).__init__(*args, **kwargs)

        # if not categories:
        #     raise CloseSpider('Received no categories!')
        # else:
        #     self.categories = categories
        # self.start_urls = ['https://www.farfetch.com/shopping/kids/items.aspx', 'https://www.farfetch.com/shopping/women/items.aspx']
        self.start_urls = ['https://www.macys.com/']

###########################################################

    def start_requests(self):
        for url in self.start_urls:
            yield Request(url, callback=self.parseCat)

###########################################################

    def parseCat(self, response):

        cats = []

        neededLabelList = ['WOMEN', 'MEN', 'SHOES', 'HANDBAGS', 'BEAUTY', 'WATCHES', 'JEWELRY']

        for neededLabel in neededLabelList:
            xpathStr = '//*[@aria-label="%s"]' % neededLabel
            tempBasicCats = response.xpath(xpathStr)

            for basicCats in tempBasicCats:
                hrefList = basicCats.xpath('.//*[@class="flexLabelLinksContainer"]/li/a')#.extract()

                for hrefSelector in hrefList:
                    ttt = hrefSelector.xpath('.//text()').extract_first()
                    if ttt.lower().count('all ') > 0 and ttt.lower().index('all ') == 0:
                        continue
                    href = hrefSelector.xpath('.//@href').extract_first()
                    if(href and not cats.__contains__(href)):
                        cats.append(href)

            pass

        if cats.__len__() == 0:
            print 'have no cats url'
            return

        print 'category urls count : ' + str(cats.__len__())

        print 'start'

        i = 1
        for cat_url in cats:
            print str(i) + ": " + cat_url
            yield Request('https://www.macys.com' + cat_url, callback=self.parseVal1)
            i += 1


        # ------------------- test -----------------------#
        # yield Request('https://www.farfetch.com/shopping/women/sale/clothing-1/items.aspx', callback=self.parseVal1)
        # yield Request('https://www.macys.com' + cats[11], callback=self.parseVal1)
        # yield Request('https://www.farfetch.com' + cats[18], callback=self.parseVal1)
        # yield Request('https://www.farfetch.com' + cats[33], callback=self.parseVal1)
        # -----------------------------------------------#
    def parseVal1(self, response):
        
        products = response.xpath('//*[@class="productThumbnail"]')

        if len(products) == 0:
            print "have no products"
            return

        print 'products count : ' + str(len(products))

        i = 0

        for product in products:
            href = product.xpath('.//div/a/@href').extract_first().strip()

            store_id = ''

            if product.xpath('.//*[@class="thumbnailImage"]/@data-src').re(r'[\d]+'):
                store_id = str(product.xpath('.//*[@class="thumbnailImage"]/@data-src').re(r'[\d]+')[1])
            elif product.xpath('.//*[@class="thumbnailImage"]/@src').re(r'[\d]+'):
                store_id = str(product.xpath('.//*[@class="thumbnailImage"]/@src').re(r'[\d]+')[1])
            else:
                continue
            # product_id = str(product.xpath('.//@id').extract_first())
            image_link = product.xpath('.//*[@class="thumbnailImage"]/@src').extract_first().strip()

            i += 1

            yield Request('https://www.macys.com' + href, callback=self.parseVal2, meta={'store_id': store_id,
                                                                                     'image_link': image_link})

        # # ------------------- test -----------------------#
        # href = products[0].xpath('.//div/a/@href').extract_first().strip()
        #
        # google_product_category = str(href.split('&')[-1].split('=')[-1].strip())
        # try:
        #     store_id = str(products[20].xpath('.//*[@class="thumbnailImage"]/@data-src').re(r'[\d]+')[1])
        # except:
        #     pass
        # # product_id = str(products[0].xpath('.//@id').extract_first())
        # image_link = products[20].xpath('.//*[@class="thumbnailImage"]/@src').extract_first().strip()
        # #
        # yield Request('https://www.macys.com/shop/product/lauren-ralph-lauren-satin-pajama-set?ID=4959646&CategoryID=59737', callback=self.parseVal2, meta={'store_id': store_id,
        #                                                                              'image_link': image_link})
        ############//////////////////////////////////////////######################


        # # next page
        nextSelector = response.xpath('//*[@class="nextPage "]')
        if not nextSelector:
            nextSelector = response.xpath('//*[@class="nextPage"]')
        if nextSelector:
            nextSelector = nextSelector[0]
            try:
                nextHref = nextSelector.xpath('.//a/@href').extract_first()
                if nextHref:
                    yield Request('https://www.macys.com' + nextHref, callback=self.parseVal1)
            except:
                pass
        #-------------------------------------------------#

    def parseVal2(self, response):

        # productSeoInfo = loads(response.xpath('//*[@id="productSEOData"]/text()').extract_first())

        productMainInfo = loads(response.xpath('//*[@id="productMainData"]/text()').extract_first(), strict=False)

        item = {}

        item['product_id'] = productMainInfo['id']#response.meta['product_id']
        item['store_id'] = response.meta['store_id']
        item['image_link'] = productMainInfo['imageUrl']#response.meta['image_link'].encode('ascii','ignore')
        item['link'] = response.url#response.meta['link'].encode('ascii','ignore')
        item['google_product_category'] = productMainInfo['categoryId']#response.meta['google_product_category']

        brand = productMainInfo['brandName']
        if not brand:
            brand = response.xpath('//*[@class="brandNameLink hidden"]/text()').extract_first()
        item['brand'] = brand

        title = productMainInfo['shortDescription']
        if not title:
            title = response.xpath('//*[@class="productName hidden"]/text()').extract_first()
        item['title'] = title

        price = ''
        try:
            price = productMainInfo['salePrice']
        except:
            pass
            # try:
            #     price = productSeoInfo['offers']['price']
            # except:
            #     price = productSeoInfo['offers'][0]['price']
        item['price'] = str(price).split('-')[0]
        # if price:
        #     price[0] = price[0].replace(',', '')
        #     item['price'] = price[0]
        item['description'] = ''
        try:
            item['description'] = productMainInfo['productDescription']['longDescription']
        except:
            item['description'] = productMainInfo['description']
        item['color'] = productMainInfo['selectedColor']

        genderTemp = productMainInfo['breadCrumbCategory'].lower()
        gender = 'Unisex'
        if genderTemp.count('women') > 0:
            gender = 'Women'
        else:
            gender = 'Men'
        item['gender'] = gender


        # item = {}
        #
        # item['product_id'] = productInfo['id'] if 'id' in productInfo.keys() else ''
        # item['store_id'] = productInfo['storeId'] if 'storeId' in productInfo.keys() else ''
        # item['brand'] = response.meta['brand'].encode('ascii','ignore')
        # item['title'] = response.meta['title'].encode('ascii','ignore')
        #
        # item['image_link'] = productInfo['imageUrl'] if 'imageUrl' in productInfo.keys() else ''
        # item['link'] = productInfo['url'] if 'url' in productInfo.keys() else ''
        # item['price'] = productInfo['unit_sale_price'] if 'unit_sale_price' in productInfo.keys() else ''
        # item['category'] = productInfo['category'] if 'category' in productInfo.keys() else ''
        # item['description'] = productInfo['description'].encode('ascii','ignore') if 'description' in productInfo.keys() else ''
        # item['color'] = productInfo['color'] if 'color' in productInfo.keys() else ''
        # item['gender'] = productInfo['gender'] if 'gender' in productInfo.keys() else ''
        # item['categoryId'] = productInfo['categoryId'] if 'categoryId' in productInfo.keys() else ''



        yield item


