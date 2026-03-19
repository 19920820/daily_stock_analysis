import os, requests

# 1. 获取飞书访问令牌
def get_token():
    url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
    payload = {"app_id": os.getenv("FEISHU_APP_ID"), "app_secret": os.getenv("FEISHU_APP_SECRET")}
    return requests.post(url, json=payload).json().get("tenant_access_token")

# 2. 读取表格记录并更新文件
def sync():
    token = get_token()
    url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{os.getenv('FEISHU_APP_TOKEN')}/tables/{os.getenv('FEISHU_TABLE_ID')}/records"
    headers = {"Authorization": f"Bearer {token}"}
    records = requests.get(url, headers=headers).json().get("data", {}).get("items", [])

    if not records: return

    # 提取股票代码并写入本地 stock_list.txt
    stocks = [r['fields']['stock_code'] for r in records if 'stock_code' in r['fields']]
    with open("stock_list.txt", "w") as f:
        f.write(",".join(stocks))
    print(f"同步成功: {stocks}")

if __name__ == "__main__":
    sync()
