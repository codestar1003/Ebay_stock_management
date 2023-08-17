import environ

from pathlib import Path
from ebaysdk.trading import Connection

def revise_item():
    app_id = "YoshikoI-test-PRD-e1b37d283-3b249a87"
    dev_id = "0cafa9d6-d905-42dd-ac15-0c1ce50d24b5"
    cert_id = "PRD-53724fcb2ed7-252c-462a-b600-af4b"
    ebay_token = "v^1.1#i^1#I^3#p^3#f^0#r^1#t^Ul4xMF8zOjdBMTE1RjJCMkZGMjhDNDc0OEFBRTJFNDMxNTQ4NDY1XzNfMSNFXjI2MA=="

    item_number = "364125180258"
    
    api = Connection(appid=app_id, devid=dev_id, certid=cert_id, token=ebay_token, config_file=None)
            
    item = {
        'Item': {
            'ItemID': item_number.strip(),
            'Quantity': "0"
        }
    }

    # api = Connection(appid=request.user.app_id, devid=request.user.dev_id, certid=request.user.cert_id, token=request.user.ebay_token, config_file=None)
    # item = {
    #     'Item': {
    #         'ItemID': product.item_number.strip(),
    #         'SKU': sku,
    #         'StartPrice': sell_price,
    #         'Quantity': quantity,
    #         'PrimaryCategory': {'CategoryID': category},
    #         'SellerProfiles': {
    #             'SellerShippingProfile': {
    #                 'ShippingProfileID': shipping_policy.profile_id,
    #             },
    #         }
    #     }
    # }
    api.execute('ReviseItem', item)

def main():
    revise_item()

if __name__ == '__main__':
    main()
