import os, requests, json

def get_token():
    # 打印环境变量是否存在（不要打印具体值，保护隐私）
    print(f"检查环境变量: APP_ID={'设置了' if os.getenv('FEISHU_APP_ID') else '缺失'}, APP_SECRET={'设置了' if os.getenv('FEISHU_APP_SECRET') else '缺失'}")
    
    url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
    payload = {"app_id": os.getenv("FEISHU_APP_ID"), "app_secret": os.getenv("FEISHU_APP_SECRET")}
    try:
        res = requests.post(url, json=payload, timeout=10).json()
        token = res.get("tenant_access_token")
        if not token:
            print(f"❌ Token 获取失败! 错误响应: {res}")
        else:
            print("✅ Token 获取成功")
        return token
    except Exception as e:
        print(f"❌ 请求 Token 发生异常: {e}")
        return None

def sync():
    token = get_token()
    if not token: return

    app_token = os.getenv("FEISHU_APP_TOKEN")
    table_id = os.getenv("FEISHU_TABLE_ID")
    
    # 增加调试信息
    print(f"正在读取表格: AppToken={app_token[:5]}***, TableID={table_id}")
    
    url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{app_token}/tables/{table_id}/records?page_size=100"
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(url, headers=headers, timeout=10).json()
        
        # 1. 检查 API 状态码
        if response.get("code") != 0:
            print(f"❌ 表格读取失败! 错误码: {response.get('code')}, 错误信息: {response.get('msg')}")
            if response.get("code") == 99991663:
                print("💡 提示：这通常是‘没有阅读权限’，请在多维表格右上角‘...’中添加应用。")
            return

        # 2. 检查记录条数
        records = response.get("data", {}).get("items", [])
        print(f"📊 接口返回记录总数: {len(records)}")

        stocks = []
        for index, r in enumerate(records):
            fields = r.get('fields', {})
            # 打印第一条记录的所有列名，帮你确认字段到底叫什么
            if index == 0:
                print(f"🔍 检测到表格列名有: {list(fields.keys())}")
            
            # 尝试多种可能的字段名（增加容错）
            code = fields.get('stock_code') or fields.get('股票代码') or fields.get('code')
            if code:
                stocks.append(str(code).strip())
        
        # 3. 写入文件
        if stocks:
            content = ",".join(stocks)
            with open("stock_list.txt", "w", encoding="utf-8") as f:
                f.write(content)
            print(f"🚀 同步成功! 已写入 {len(stocks)} 只股票: {content}")
        else:
            print("⚠️ 警告：虽然读到了记录，但没在这些记录里找到名为 'stock_code' 的列数据。")

    except Exception as e:
        print(f"❌ 同步过程发生未知异常: {e}")

if __name__ == "__main__":
    sync()
