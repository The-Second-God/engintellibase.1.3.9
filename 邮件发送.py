import smtplib
import schedule
import time
from email.mime.text import MIMEText
from email.header import Header
# 修正1：补充导入date类，解决核心的属性报错问题
from datetime import datetime, date

# 配置信息 - 完全保留你的原有配置，仅修正了误导性注释
EMAIL_CONFIG = {
    'sender': 'xxxxxxxx@163.com',  # 你的网易163邮箱
    'auth_code': 'xxxxxxxxxxx',  # 网易邮箱SMTP授权码
    'receiver': 'xxxxxxxxxxxx@qq.com',  # 接收人的QQ邮箱
    'smtp_server': 'smtp.163.com',  # 网易163邮箱SMTP服务器
    'smtp_port': 465  # SSL加密端口，固定无需修改
}

# 修正2：把打卡起始日期提为全局常量，方便修改，避免函数内重复生成
CHECKIN_START_DATE = date(2026, 3, 8)

# 每日发送的打卡信息内容
def get_checkin_content():
    """生成每日打卡信息内容"""
    # 修正3：统一单次获取今日日期，避免跨零点日期不一致、重复调用问题
    today_date = date.today()
    today_str = today_date.strftime("%Y年%m月%d日")
    # 计算打卡第几天（起始日算作第1天）
    delta = today_date - CHECKIN_START_DATE
    day_count = delta.days + 1

    content = f"""
    <h2>今日打卡</h2>
    <p>进度：day{day_count}</p>
    <p>日期：{today_str}</p>
    <p>状态：已完成今日打卡 ✅</p>
    """
    return content

def send_checkin_email():
    """发送打卡邮件"""
    try:
        # 构建邮件内容
        message = MIMEText(get_checkin_content(), 'html', 'utf-8')
        message['From'] = Header(f"<{EMAIL_CONFIG['sender']}>")
        message['To'] = Header(f"<{EMAIL_CONFIG['receiver']}>")
        message['Subject'] = Header(f"每日blue打卡{date.today()}", 'utf-8')

        # 连接SMTP服务器并发送邮件
        with smtplib.SMTP_SSL(EMAIL_CONFIG['smtp_server'], EMAIL_CONFIG['smtp_port']) as server:
            server.login(EMAIL_CONFIG['sender'], EMAIL_CONFIG['auth_code'])
            server.sendmail(
                EMAIL_CONFIG['sender'],
                EMAIL_CONFIG['receiver'],
                message.as_string()
            )
        
        print(f"{datetime.now()} - 打卡邮件发送成功！")
        return True
    
    except smtplib.SMTPException as e:
        print(f"{datetime.now()} - SMTP邮件发送失败: {str(e)}")
        return False
    except Exception as e:
        print(f"{datetime.now()} - 程序异常: {str(e)}")
        return False

def setup_daily_schedule(hour=9, minute=0):
    """设置每日定时发送任务"""
    # 每天指定时间执行发送邮件函数
    schedule.every().day.at(f"{hour:02d}:{minute:02d}").do(send_checkin_email)
    
    print(f"✅ 每日打卡邮件发送任务已设置，将在每天{hour:02d}:{minute:02d}自动发送")
    print("📌 程序运行中，按 Ctrl+C 可退出...")
    
    # 保持程序运行，检查定时任务
    while True:
        schedule.run_pending()
        time.sleep(60)  # 每分钟检查一次

if __name__ == "__main__":
    # 重要提示：使用前请先开启网易邮箱的SMTP服务
    # 1. 网页登录网易163邮箱 → 设置 → POP3/SMTP/IMAP
    # 2. 开启SMTP服务，按提示获取授权码，填入上方配置
    
    #测试发送邮件（仅一次）（调试用）
    #send_checkin_email()
    
    setup_daily_schedule(hour=9, minute=0)