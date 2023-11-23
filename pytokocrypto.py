# Copyright 2023 - Ikhsan Maulana

import requests
import time
import hmac
import hashlib
import json
from urllib.parse import urlencode
from datetime import datetime

BASE_URL = "https://www.tokocrypto.com"
GENERAL_CHECK_SERVER_TIME_URL = "/open/v1/common/time"
GENERAL_SUPPORTED_TRADING_SYMBOL_URL = "/open/v1/common/symbols"

MARKET_ORDER_BOOK_URL = "/open/v1/market/depth"
MARKET_ORDER_BOOK_BINANCE_URL = "https://api.binance.com/api/v3/depth"
MARKET_RECENT_TRADES_LIST_URL = "/open/v1/market/trades"
MARKET_RECENT_TRADES_LIST_BINANCE_URL = "https://api.binance.com/api/v3/trades"
MARKET_AGGREGATE_TRADE_LIST_URL = "/open/v1/market/agg-trades"
MARKET_AGGREGATE_TRADE_LIST_BINANCE_URL = "https://api.binance.com/api/v3/aggTrades"
MARKET_CANDLESTICK_DATA_URL = "/open/v1/market/klines"
MARKET_CANDLESTICK_DATA_BINANCE_URL = "https://api.binance.com/api/v1/klines"

ACCOUNT_NEW_ORDER_URL = "/open/v1/orders"
ACCOUNT_QUERY_ORDER_URL = "/open/v1/orders/detail"
ACCOUNT_CANCEL_ORDER_URL = "/open/v1/orders/cancel"
ACCOUNT_ALL_ORDER = "/open/v1/orders"
ACCOUNT_NEW_OCO = "/open/v1/orders/oco"
ACCOUNT_INFORMATION_URL = "/open/v1/account/spot"
ACCOUNT_ASSET_INFORMATION_URL = "/open/v1/account/spot/asset"
ACCOUNT_TRADE_LIST_URL = "/open/v1/orders"

WALLET_WITHDRAW_URL = "/open/v1/withdraws"
WALLET_WITHDRAW_HISTORY_URL = "/open/v1/withdraws"
WALLET_DEPOSIT_HISTORY_URL = "/open/v1/deposits"
WALLET_DEPOSIT_ADDRESS_URL = "/open/v1/deposits/address"


class BaseTokoCrypto:
    def __init__(self, api_key: str = None, secret_key: str = None):
        self.__api_key = api_key
        self.__secret_key = secret_key
        self.__headers = {"X-MBX-APIKEY": self.__api_key}
        self.__symbol_type = self.__get_symbol_type()

    def __get_symbol_type(self):
        response = self.general_supported_trading_symbol()
        symbol_type = {data["symbol"]: data["type"] for data in response.json()["data"]["list"]}
        return symbol_type

    def __request(self, **kwargs):
        payload = kwargs["payload"]
        endpoint_url = kwargs["endpoint_url"]
        method = kwargs["method"]
        signed = kwargs["signed"]

        parameter = dict()
        [parameter.update({key: payload[key]}) for key in payload.keys() if payload[key]]

        signature = self.__hash_signature(parameter)
        parameter['signature'] = signature

        url = endpoint_url

        request_payload = {
            "url": url,
            "params": parameter
        }
        # accessing account endpoint that required to be SIGNED (apiKey and secretKey)
        if signed:
            request_payload["headers"] = self.__headers

        if method == "get":
            response = requests.get(**request_payload)
        elif method == "post":
            response = requests.post(**request_payload)
        elif method == "put":
            response = requests.put(**request_payload)
        elif method == "delete":
            response = requests.delete(**request_payload)

        response.raise_for_status()
        return response

    def __hash_signature(self, parameter: dict) -> str:
        # hashing secret_key to signature code using HMAC SHA256
        query_string = urlencode(parameter, True)
        m = hmac.new(self.__secret_key.encode("utf-8"), query_string.encode("utf-8"), hashlib.sha256)
        signature = m.hexdigest()
        return signature
        
    @staticmethod
    def general_check_server_time() -> datetime:
        # Test connectivity to the Rest API and get the current server time.
        endpoint_url = BASE_URL + GENERAL_CHECK_SERVER_TIME_URL

        url = BASE_URL + endpoint_url
        response = requests.get(url=url)
        response.raise_for_status()
        print("Server is Connect")
        timestamp = int(response.json()['timestamp']) / 1000
        dt_object = datetime.fromtimestamp(timestamp)
        return dt_object
        
    @staticmethod
    def general_supported_trading_symbol():
        # This endpoint returns all Exchange's supported trading symbol.
        url = BASE_URL + GENERAL_SUPPORTED_TRADING_SYMBOL_URL
        response = requests.get(url=url)
        return response

    def market_order_book(self, symbol: str, limit: int = None):
        # Send in a new order.
        if self.__symbol_type[symbol] == 1:
            endpoint_url = MARKET_ORDER_BOOK_BINANCE_URL
            symbol = symbol.replace("_", "")
        else:
            endpoint_url = BASE_URL + MARKET_ORDER_BOOK_URL

        payload = {
            "symbol": symbol,
            "limit": limit
        }

        response = self.__request(method="get", payload=payload, endpoint_url=endpoint_url, signed=False)
        return response

    def market_recent_trades_list(self, symbol: str, from_id: int = None, limit: int = None):
        # Send in a new order.
        if self.__symbol_type[symbol] == 1:
            endpoint_url = MARKET_RECENT_TRADES_LIST_BINANCE_URL
            symbol = symbol.replace("_", "")
        else:
            endpoint_url = BASE_URL + MARKET_RECENT_TRADES_LIST_URL

        payload = {
            "symbol": symbol,
            "fromId": from_id,
            "limit": limit
        }

        response = self.__request(method="get", payload=payload, endpoint_url=endpoint_url, signed=False)
        return response

    def market_aggregate_trade_list(self, symbol: str, from_id: int = None, start_time: int = None,
                                    end_time: int = None, limit: int = None):
        # Send in a new order.
        if self.__symbol_type[symbol] == 1:
            endpoint_url = MARKET_AGGREGATE_TRADE_LIST_BINANCE_URL
            symbol = symbol.replace("_", "")
        else:
            endpoint_url = BASE_URL + MARKET_AGGREGATE_TRADE_LIST_URL

        payload = {
            "symbol": symbol,
            "fromId": from_id,
            "startTime": start_time,
            "endTime": end_time,
            "limit": limit
        }

        response = self.__request(method="get", payload=payload, endpoint_url=endpoint_url, signed=False)
        return response

    def market_candlestick_data(self, symbol: str, interval: str, start_time: int = None, end_time: int = None,
                                limit: int = 500):
        # Send in a new order.
        """
        :param symbol:
        :param interval: Kline/Candlestick chart intervals: m -> minutes; h -> hours; d -> days; w -> weeks; M -> months
        1m 3m 5m  15m 1h 2h 4h 6h 8h 12h 1d 3d 1w 1M
        :param start_time: If startTime and endTime are not sent, the most recent kline are returned.
        :param end_time: If startTime and endTime are not sent, the most recent kline are returned.
        :param limit:
        :return: response
        """
        #Send in a new order.
        if self.__symbol_type[symbol] == 1:
            endpoint_url = MARKET_CANDLESTICK_DATA_BINANCE_URL
            symbol = symbol.replace("_", "")
        else:
            endpoint_url = BASE_URL + MARKET_CANDLESTICK_DATA_URL
 
        payload = {
            "symbol": symbol,
            "interval": interval,
            "startTime": start_time,
            "endTime": end_time,
            "limit": limit
        }

        response = self.__request(method="get", payload=payload, endpoint_url=endpoint_url, signed=False)
        return response

    def account_new_order(self, symbol: str, side: int, type_: int, time_in_force: int = None, quantity: str = None,
                          quote_order_qty: str = None, price: str = None, client_id: str = None, stop_price: str = None,
                          iceberg_qty: str = None, recv_window: int = 5000) -> json:
        # Check an order's status.
        """
        :param symbol: Coin Symbol. You can check list of available symbol on TokoCrypto class method
        :param side: 0,1
        Order side (side):
        0 BUY
        1 SELL
        :param type_: 1,2,4,6
        1	quantity, price
        2	quantity (sell) or quoteOrderQty (buy)
        3	quantity, stopPrice
        4	quantity, price, stopPrice
        5	quantity, stopPrice
        6	quantity, price, stopPrice
        7	quantity, price
        :param time_in_force: 1,2,3,4
        timeInForce Value	Content
        1	GTC-Good Till Cancel
        2	IOC-Immediate or Cancel
        3	FOK-Fill or Kill
        4	GTX-Good Till Crossing
        :param quantity: aka lots
        :param quote_order_qty:
        MARKET orders using quoteOrderQty specifies the amount the user wants to spend (when buying) of the quote asset;
        the correct quantity will be determined based on the market liquidity and quoteOrderQty.
        :param price: Order book price
        :param client_id: Client's custom ID for the order, Server does not check it's uniqueness.
        Automatically generated if not sent.
        :param stop_price: Used with STOP_LOSS, STOP_LOSS_LIMIT, TAKE_PROFIT, and TAKE_PROFIT_LIMIT orders.
        :param iceberg_qty: Used with LIMIT, STOP_LOSS_LIMIT, and TAKE_PROFIT_LIMIT to create an iceberg order.
        :param recv_window: The value cannot be greater than 60000
        :return: returning json file of response
        """
        endpoint_url = BASE_URL + ACCOUNT_NEW_ORDER_URL

        timestamp = int(time.time() * 1000)
        payload = {
            "symbol": symbol,
            "side": side,
            "type": type_,
            "timeInForce": time_in_force,
            "quantity": quantity,
            "quoteOrderQty": quote_order_qty,
            "price": price,
            "clientId": client_id,
            "stopPrice": stop_price,
            "icebergQty": iceberg_qty,
            "recvWindow": recv_window,
            "timestamp": timestamp
        }

        response = self.__request(method="post", payload=payload, endpoint_url=endpoint_url, signed=True)
        return response.json()

    def account_query_order(self, order_id: int, client_id: str = None, recv_window: int = 5000):
        # Send in a new order.
        """
        :param order_id: You can check the
        :param client_id: Client's custom ID for the order, Server does not check it's uniqueness. Automatically generated if not sent.
        :return:
        """
        endpoint_url = BASE_URL + ACCOUNT_QUERY_ORDER_URL

        timestamp = int(time.time() * 1000)
        payload = {
            "orderId": order_id,
            "clientId": client_id,
            "recvWindow": recv_window,
            "timestamp": timestamp
        }

        response = self.__request(method="get", payload=payload, endpoint_url=endpoint_url, signed=True)
        return response

    def account_cancel_order(self, order_id: int, recv_window: int = 5000):
        # Send in a new order.
        """
        :param order_id: You can check the
        """
        endpoint_url = BASE_URL + ACCOUNT_CANCEL_ORDER_URL

        timestamp = int(time.time() * 1000)
        payload = {
            "orderId": order_id,
            "recvWindow": recv_window,
            "timestamp": timestamp
        }

        response = self.__request(method="post", payload=payload, endpoint_url=endpoint_url, signed=True)
        return response

    def account_all_order(self, symbol: str, side: int = None, type_: int = None, start_time: int = None,
                          end_time: int = None, from_id: str = None, direct: int = None, limit: int = None,
                          recv_window: int = 5000):
        # Get all account orders; active, canceled, or filled.
        """
        :param symbol:
        :param side: 0,1
        Order side (side):
        0 BUY
        1 SELL
        :param type_: 1,2,4,6
        1	quantity, price
        2	quantity (sell) or quoteOrderQty (buy)
        3	quantity, stopPrice
        4	quantity, price, stopPrice
        5	quantity, stopPrice
        6	quantity, price, stopPrice
        7	quantity, price
        :param start_time:
        :param end_time:
        :param from_id: start order ID the searching to begin with.
        :param direct: searching direction: prev - in ascending order from the start order ID; next - in descending order from the start order ID
        :param limit: Default 500; max 1000.
        :return:
        """
        endpoint_url = BASE_URL + ACCOUNT_ALL_ORDER

        timestamp = int(time.time() * 1000)
        payload = {
            "symbol": symbol,
            "type": type_,
            "side": side,
            "startTime": start_time,
            "endTime": end_time,
            "fromId": from_id,
            "direct": direct,
            "limit": limit,
            "recvWindow": recv_window,
            "timestamp": timestamp
        }

        response = self.__request(method="get", payload=payload, endpoint_url=endpoint_url, signed=True)
        return response

    def account_new_oco(self, symbol: str, side: int, quantity: str, price: str, stop_client_id: str = None,
                        stop_price: str = None, list_client_d: str = None, limit_client_id: str = None,
                        stop_limit_price: str = None, recv_window: int = 5000):
        """
        :param symbol:
        :param side:
        :param quantity:
        :param price:
        :param stop_client_id: Client's custom ID for the stop loss/stop loss limit order, Server does not check it's uniqueness. Automatically generated if not sent.
        :param stop_price: price
        :param list_client_d: Client's custom ID for the entire orderList, Server does not check it's uniqueness. Automatically generated if not sent.
        :param limit_client_id: Client's custom ID for the limit order, Server does not check it's uniqueness. Automatically generated if not sent.
        :param stop_limit_price: Stop limit price
        :param recv_window:
        :return:
        """
        # Send in a new OCO
        endpoint_url = BASE_URL + ACCOUNT_NEW_OCO

        timestamp = int(time.time() * 1000)
        payload = {
            "symbol": symbol,
            "listClientId": list_client_d,
            "side": side,
            "quantity": quantity,
            "limitClientId	": limit_client_id,
            "price": price,
            "stopClientId": stop_client_id,
            "stopPrice": stop_price,
            "stopLimitPrice	": stop_limit_price,
            "recvWindow": recv_window,
            "timestamp": timestamp
        }

        response = self.__request(method="post", payload=payload, endpoint_url=endpoint_url, signed=True)
        return response

    def account_information(self, recv_window: int = 5000):
        # Get current account information.
        endpoint_url = BASE_URL + ACCOUNT_INFORMATION_URL

        timestamp = int(time.time() * 1000)
        payload = {
            "recvWindow": recv_window,
            "timestamp": timestamp
        }

        response = self.__request(method="get", payload=payload, endpoint_url=endpoint_url, signed=True)
        return response

    def account_asset_information(self, asset: str, recv_window: int = 5000):
        # Get current account information for a specific asset.
        endpoint_url = BASE_URL + ACCOUNT_ASSET_INFORMATION_URL

        timestamp = int(time.time() * 1000)
        payload = {
            "asset": asset,
            "recvWindow": recv_window,
            "timestamp": timestamp
        }

        response = self.__request(method="get", payload=payload, endpoint_url=endpoint_url, signed=True)
        return response

    def account_trade_list(self, symbol: str, order_id: str = None, start_time: int = None, end_time: int = None,
                           from_id: int = None, direct: int = None, rebate_status: int = None, limit: int = 500,
                           recv_window: int = 5000):
        # Get trades for a specific account and symbol.
        endpoint_url = BASE_URL + ACCOUNT_TRADE_LIST_URL

        timestamp = int(time.time() * 1000)
        payload = {
            "asset": symbol,
            "orderId": order_id,
            "startTime": start_time,
            "endTime": end_time,
            "fromId": from_id,
            "direct": direct,
            "limit": limit,
            "recvWindow": recv_window,
            "timestamp": timestamp,
            "rebateStatus": rebate_status
        }

        response = self.__request(method="get", payload=payload, endpoint_url=endpoint_url, signed=True)
        return response

    def wallet_withdraw(self, asset: str, address: str, amount: str, client_id: str = None, network: str = None,
                        address_tag: str = None, recv_window: int = 5000):
        # Submit a withdraw request.
        endpoint_url = BASE_URL + WALLET_WITHDRAW_URL

        timestamp = int(time.time() * 1000)
        payload = {
            "asset": asset,
            "clientId": client_id,
            "network": network,
            "address": address,
            "addressTag": address_tag,
            "amount": amount,
            "recvWindow": recv_window,
            "timestamp": timestamp
        }

        response = self.__request(method="get", payload=payload, endpoint_url=endpoint_url, signed=True)
        return response.json()

    def wallet_withdraw_history(self, asset: str = None, status: int = None, from_id: int = None,
                                start_time: int = None, end_time: int = None, recv_window: int = 5000):
        # Fetch withdraw history.
        endpoint_url = BASE_URL + WALLET_WITHDRAW_HISTORY_URL

        timestamp = int(time.time() * 1000)
        payload = {
            "asset": asset,
            "status": status,
            "fromId": from_id,
            "startTime": start_time,
            "endTime": end_time,
            "recvWindow": recv_window,
            "timestamp": timestamp
        }

        response = self.__request(method="get", payload=payload, endpoint_url=endpoint_url, signed=True)
        return response

    def wallet_deposit_history(self, asset: str = None, status: int = None, from_id: int = None, start_time: int = None,
                               end_time: int = None, recv_window: int = 5000):
        # Fetch deposit history..
        endpoint_url = BASE_URL + WALLET_DEPOSIT_HISTORY_URL

        timestamp = int(time.time() * 1000)
        payload = {
            "asset": asset,
            "status": status,
            "fromId": from_id,
            "startTime": start_time,
            "endTime": end_time,
            "recvWindow": recv_window,
            "timestamp": timestamp
        }

        response = self.__request(method="get", payload=payload, endpoint_url=endpoint_url, signed=True)
        return response

    def wallet_deposit_address(self, asset: str, network: str, recv_window: int = 5000):
        # Fetch deposit address.
        endpoint_url = BASE_URL + WALLET_DEPOSIT_ADDRESS_URL

        timestamp = int(time.time() * 1000)
        payload = {
            "asset": asset,
            "network": network,
            "recvWindow": recv_window,
            "timestamp": timestamp
        }

        response = self.__request(method="get", payload=payload, endpoint_url=endpoint_url, signed=True)
        return response

    @property
    def api_key(self) -> str:
        return self.__api_key

    @api_key.setter
    def api_key(self, api_key: str):
        self.__api_key = api_key

    @property
    def secret_key(self) -> str:
        return self.__secret_key

    @api_key.setter
    def secret_key(self, secret_key: str):
        self.__api_key = secret_key

    @property
    def symbol_type(self) -> str:
        return self.__symbol_type
