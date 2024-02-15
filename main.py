import os
import time
import requests
from lxml import etree
from datetime import datetime
from dotenv import load_dotenv
from constants import URL, XPATH


def init() -> None:
    # 從 .env 讀取環境變數
    load_dotenv()

    # 檢查必要的環境變數是否存在
    if ("DISCORD_WEBHOOK_URL" not in os.environ):
        raise Exception("DISCORD_WEBHOOK_URL not set")

    if ("START_STA" not in os.environ):
        raise Exception("START_STA not set")

    if ("END_STA" not in os.environ):
        raise Exception("END_STA not set")

    if ("RIDE_DATE" not in os.environ):
        raise Exception("RIDE_DATE not set")

    if ("QTY" not in os.environ):
        raise Exception("QTY not set")

    if ("TRAIN_NO" not in os.environ):
        raise Exception("TRAIN_NO not set")


def main_loop(browser: requests.Session) -> None:
    try:
        while (True):
            # 先讀取個人訂票(完整)頁面一次
            res = browser.get(URL.TICKET_QUERY_PAGE)

            # 對頁面回應做解析
            content = res.content.decode()
            html = etree.HTML(content)

            # 從頁面、環境變數取得必要參數
            csrf = html.xpath(XPATH.CSRF)[0]
            start_station = os.environ.get("START_STA")
            end_station = os.environ.get("END_STA")
            ride_date = os.environ.get("RIDE_DATE")
            qty = os.environ.get("QTY")
            train_no = os.environ.get("TRAIN_NO")
            complete_token = html.xpath(XPATH.COMPLETE_TOKEN)[0]

            # 製作查詢 API Payload
            payload = {
                "_csrf": csrf,
                "custIdTypeEnum": "PERSON_ID",
                "pid": "G142740006",
                "tripType": "ONEWAY",
                "orderType": "BY_TRAIN_NO",
                "ticketOrderParamList[0].tripNo": "TRIP1",
                "ticketOrderParamList[0].startStation": start_station,
                "ticketOrderParamList[0].endStation": end_station,
                "ticketOrderParamList[0].rideDate": ride_date,
                "ticketOrderParamList[0].normalQty": qty,
                "ticketOrderParamList[0].wheelChairQty": "0",
                "ticketOrderParamList[0].parentChildQty": "0",
                "ticketOrderParamList[0].trainNoList[0]": train_no,
                "ticketOrderParamList[0].trainNoList[1]": "",
                "ticketOrderParamList[0].trainNoList[2]": "",
                "ticketOrderParamList[0].chgSeat": "true",
                "_ticketOrderParamList[0].chgSeat": "on",
                "ticketOrderParamList[0].seatPref": "NONE",
                "completeToken": complete_token
            }

            # 以 Payload 打查詢車票 API
            res = browser.post(URL.TICKET_QUERY_API, data=payload)

            # 對頁面回應做解析
            content = res.content.decode()
            html = etree.HTML(content)

            # 取得搜尋結果的 HTML 表格
            search_result = html.xpath(XPATH.RESULT_TABLE)

            # 取得現在時間戳
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            if (not search_result):
                # 若沒有搜尋到任何空位結果，印出 Log
                msg = "[{}] {} - {} {}班次列車 目前無空位".format(
                    timestamp, start_station, end_station, train_no)
                print(msg)
            else:
                # 若有搜尋到任何空位結果，印出 Log 並通知 Discord 頻道
                msg = "[{}] {} - {} {}班次列車 目前有空位".format(
                    timestamp, start_station, end_station, train_no)
                requests.post(os.environ.get(
                    "DISCORD_WEBHOOK_URL"), json={"content": msg})
                print(msg)

            # 每隔 30 秒檢查一次
            time.sleep(30)

    except KeyboardInterrupt:
        print("退出程式")
        exit(0)


if __name__ == '__main__':
    # 初始化
    init()

    # 主迴圈
    browser = requests.Session()
    main_loop(browser)
