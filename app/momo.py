import json
import uuid
import requests
import hmac
import hashlib
from app import app


def get_payment_url(order_id, amount):
    endpoint = app.config['MOMO_PAYMENT_URL']
    accessKey = app.config['MOMO_ACCESS_KEY']
    secretKey = app.config['MOMO_SECRET_KEY']
    orderInfo = "abcdefghijklmnopqrstuvwxyz"
    partnerCode = "MOMO"
    redirectUrl = app.config['MOMO_RETURN_URL']
    ipnUrl = "https://webhook.site/b3088a6a-2d17-4f8d-a383-71389a6c600b"
    amount = str(int(amount))
    orderId = str(order_id)
    requestId = str(uuid.uuid4())
    extraData = ""
    partnerName = "MoMo Payment"
    requestType = "payWithMethod"
    storeId = "Test Store"
    orderGroupId = ""
    autoCapture = True
    lang = "vi"
    orderGroupId = ""

    rawSignature = "accessKey=" + accessKey + "&amount=" + amount + "&extraData=" + extraData + "&ipnUrl=" + ipnUrl + "&orderId=" + orderId \
                   + "&orderInfo=" + orderInfo + "&partnerCode=" + partnerCode + "&redirectUrl=" + redirectUrl \
                   + "&requestId=" + requestId + "&requestType=" + requestType

    h = hmac.new(bytes(secretKey, 'ascii'), bytes(rawSignature, 'ascii'), hashlib.sha256)
    signature = h.hexdigest()

    data = {
        'partnerCode': partnerCode,
        'orderId': orderId,
        'partnerName': partnerName,
        'storeId': storeId,
        'ipnUrl': ipnUrl,
        'amount': amount,
        'lang': lang,
        'requestType': requestType,
        'redirectUrl': redirectUrl,
        'autoCapture': autoCapture,
        'orderInfo': orderInfo,
        'requestId': requestId,
        'extraData': extraData,
        'signature': signature,
        'orderGroupId': orderGroupId
    }
    data = json.dumps(data)

    clen = len(data)
    response = requests.post(endpoint, data=data,
                             headers={'Content-Type': 'application/json', 'Content-Length': str(clen)})
    res = response.json()
    return res['payUrl']
