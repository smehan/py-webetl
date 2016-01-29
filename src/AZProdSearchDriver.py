from AZProdSearch import *
from amazonproduct import API


api = API(locale='us')
root = api.item_lookup('0136042597', IdType='ISBN',
                     SearchIndex='Books', ResponseGroup='Reviews', ReviewPage=1)