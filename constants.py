class URL(enumerate):
    TICKET_QUERY_PAGE = "https://tip.railway.gov.tw/tra-tip-web/tip/tip001/tip123/query"
    TICKET_QUERY_API = "https://tip.railway.gov.tw/tra-tip-web/tip/tip001/tip123/queryTrain"

class XPATH(enumerate):
    CSRF = "/html/body/div[4]/div[5]/div/form/input[1]/@value"
    COMPLETE_TOKEN = "/html/body/div[4]/div[5]/div/form/input[2]/@value"
    RESULT_TABLE = "/html/body/div[1]/form[1]/div[1]/table"

