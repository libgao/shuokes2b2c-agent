import pandas as pd
import random
from datetime import datetime, timedelta
import os

random.seed(42)
os.makedirs("data", exist_ok=True)

# 1. 学员表
students = []
names = ["王小明","李思思","张一诺","陈子轩","刘雨桐","赵浩然","孙可欣","周梓涵",
         "吴俊杰","郑欣怡","冯宇轩","何佳琪","高子墨","林语嫣","黄泽宇","徐若曦",
         "马晨曦","朱一凡","胡诗涵","郭子豪"]
grades = ["二年级","三年级","四年级","五年级","六年级"]
emotions = ["正常","中性","焦虑","不满","提退费","投诉"]
channels = ["渠道A","渠道B","渠道C","渠道D"]
consultants = ["小B-01","小B-02","小B-03"]

for i in range(1, 21):
    students.append({
        "student_id": f"S{i:03d}", "name": names[i-1], "grade": random.choice(grades),
        "remaining_hours": random.choice([24, 36, 48, 60, 80]),
        "unit_progress": round(random.uniform(0.15, 0.85), 2),
        "last_booking_days": random.choice([1,3,5,8,10,12,15,20]),
        "fail_bookings_7d": random.choice([0,0,1,2,3,4,5]),
        "practice_miss_days": random.choice([0,1,2,3,5,7,10]),
        "report_opened": random.choice([0,1]), "emotion_tag": random.choice(emotions),
        "channel": random.choice(channels), "consultant": random.choice(consultants),
    })
students_df = pd.DataFrame(students)
students_df.to_csv("data/students.csv", index=False, encoding="utf-8-sig")

# 2. 学习记录表
logs = []
today = datetime(2026, 11, 10)
for _, s in students_df.iterrows():
    for d in range(13, -1, -1):
        date = today - timedelta(days=d)
        booked = random.choice([0,1])
        fail = random.choice([0,0,0,1,2])
        consumed = random.choice([0,1,1,2]) if booked else 0
        logs.append({
            "student_id": s["student_id"], "date": date.strftime("%Y-%m-%d"),
            "booked": booked, "booking_fail": fail, "hours_consumed": consumed,
            "practice_done": random.choice([0,1]), "report_opened": random.choice([0,1]),
        })
pd.DataFrame(logs).to_csv("data/learning_logs.csv", index=False, encoding="utf-8-sig")

# 3. 规则表
rules = [
    {"rule_id":"R1","signal":"连续未约课","condition":"last_booking_days>=10","reason_candidates":"时段冲突|动力衰减","action":"电话沟通","collaborator":"社群老师","sla_hours":48,"allowed_script":"未来14天内可约，每周至少提供3个可选时段","forbidden_script":"随时退|保证固定外教|保证提分"},
    {"rule_id":"R2","signal":"约课失败","condition":"fail_bookings_7d>=3","reason_candidates":"老师不匹配|时段不足","action":"协调时段与老师","collaborator":"排课专员","sla_hours":24,"allowed_script":"未满300课时按学情匹配老师","forbidden_script":"保证约到某老师|随时退"},
    {"rule_id":"R3","signal":"耗课滞后","condition":"unit_progress>=0.5且耗课<40%","reason_candidates":"难度不适|节奏问题","action":"与老师确认难度","collaborator":"外教/中教","sla_hours":72,"allowed_script":"按学情调整练习节奏","forbidden_script":"保证提分|保证效果"},
    {"rule_id":"R4","signal":"练习断更","condition":"practice_miss_days>=5","reason_candidates":"动力衰减|任务过重","action":"推轻量任务","collaborator":"社群老师","sla_hours":48,"allowed_script":"社群每日跟课，任务可拆分","forbidden_script":"保证效果|保证提分"},
    {"rule_id":"R5","signal":"情绪信号","condition":"emotion_tag in (提退费,投诉)","reason_candidates":"服务响应|承诺落差","action":"学情复盘+方案调整","collaborator":"主管","sla_hours":8,"allowed_script":"未消耗课时按合同梯度扣费，7个工作日内完成退费工单","forbidden_script":"无条件退费|随时退"},
]
pd.DataFrame(rules).to_csv("data/rules.csv", index=False, encoding="utf-8-sig")

# 4. 任务表
tasks = []
signals = ["连续未约课","约课失败","耗课滞后","练习断更","情绪信号"]
statuses = ["待处理","处理中","已关闭","已升级"]
collaborators = ["社群老师","排课专员","外教/中教","主管"]
reasons = ["时段冲突","老师不匹配","难度不适","动力衰减","服务响应","承诺落差"]

for i in range(1, 16):
    s = students_df.iloc[i-1]
    sig = signals[(i-1) % 5]
    created = today - timedelta(days=random.randint(0, 5))
    status = random.choice(statuses)
    first_resp = None
    closed = None
    if status in ["处理中","已关闭","已升级"]:
        first_resp = created + timedelta(hours=random.randint(1, 20))
    if status in ["已关闭","已升级"]:
        closed = first_resp + timedelta(hours=random.randint(2, 48))
    tasks.append({
        "task_id": f"T{i:03d}", "student_id": s["student_id"], "student_name": s["name"],
        "signal": sig, "evidence": f"剩余{s['remaining_hours']}课时 · 距最后约课{s['last_booking_days']}天 · 近7天约课失败{s['fail_bookings_7d']}次 · 单元耗课{int(s['unit_progress']*100)}% · 练习断更{s['practice_miss_days']}天",
        "reason_hypothesis": random.choice(reasons), "action": random.choice(["电话沟通","协调时段与老师","与老师确认难度","推轻量任务","学情复盘+方案调整"]),
        "collaborator": random.choice(collaborators), "sla_hours": random.choice([8,24,48,72]), "status": status,
        "created_at": created.strftime("%Y-%m-%d %H:%M"),
        "first_response_at": first_resp.strftime("%Y-%m-%d %H:%M") if first_resp else "",
        "closed_at": closed.strftime("%Y-%m-%d %H:%M") if closed else "",
        "recovered_booking": random.choice([0,1]) if status == "已关闭" else 0,
        "miscommit_flag": random.choice([0,0,0,1]), "channel": s["channel"], "consultant": s["consultant"],
    })
tasks_df = pd.DataFrame(tasks)
tasks_df.to_csv("data/tasks.csv", index=False, encoding="utf-8-sig")

# 5. 回填表
feedback = []
for _, t in tasks_df.iterrows():
    if t["status"] in ["已关闭","已升级"]:
        feedback.append({
            "task_id": t["task_id"], "parent_feedback": random.choice(["已协调时段","家长情绪缓和","仍不满意","要求退费","已恢复约课"]),
            "emotion_after": random.choice(["正常","中性","焦虑","不满"]), "escalated": 1 if t["status"]=="已升级" else 0,
            "miscommit_hit": t["miscommit_flag"], "satisfaction_score": random.choice([3,4,4,5,5]),
            "recovered_booking": t["recovered_booking"],
        })
pd.DataFrame(feedback).to_csv("data/feedback.csv", index=False, encoding="utf-8-sig")

print("数据生成完成！请检查左侧 data 文件夹。")