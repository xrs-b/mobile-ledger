"""
数据库初始化脚本
"""
import sys
import os

# 添加app目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from app.database import engine, Base, get_db
from app.models import User, Category, SystemConfig, InvitationCode


def init_db():
    """初始化数据库"""
    print("🚀 开始初始化数据库...")
    
    # 创建所有表
    Base.metadata.create_all(bind=engine)
    print("✅ 数据表创建完成")
    
    # 获取数据库会话
    db = next(get_db())
    
    try:
        # 检查是否已有数据
        existing_users = db.query(User).count()
        if existing_users > 0:
            print(f"⚠️ 数据库已有 {existing_users} 个用户，跳过初始化")
            return
        
        # 创建默认邀请码
        default_invitation = InvitationCode(
            code="admin123",
            is_used=False,
            created_by=1,  # 第一个用户会使用这个邀请码
        )
        db.add(default_invitation)
        
        # 创建系统配置
        configs = [
            SystemConfig(
                config_key="default_invitation_code",
                config_value="admin123",
                description="默认邀请码"
            ),
            SystemConfig(
                config_key="max_users",
                config_value="1000",
                description="最大用户数"
            ),
            SystemConfig(
                config_key="demo_mode",
                config_value="false",
                description="演示模式"
            ),
        ]
        for config in configs:
            db.add(config)
        
        # 创建默认分类（一级）
        first_level_categories = [
            ("餐饮", "🍔", "expense"),
            ("交通", "🚗", "expense"),
            ("购物", "🛒", "expense"),
            ("居住", "🏠", "expense"),
            ("娱乐", "🎮", "expense"),
            ("教育", "📚", "expense"),
            ("医疗", "💊", "expense"),
            ("理财", "💰", "expense"),
            ("人情", "🎁", "expense"),
            ("通讯", "📱", "expense"),
            ("工作", "💼", "expense"),
            ("其他", "🎫", "expense"),
            ("收入", "💵", "income"),
        ]
        
        category_map = {}  # 保存一级分类ID
        for name, icon, ctype in first_level_categories:
            cat = Category(
                name=name,
                icon=icon,
                type=ctype,
                is_system=True,
                user_id=None,  # 系统分类
            )
            db.add(cat)
            db.flush()  # 获取ID
            category_map[f"{name}_{ctype}"] = cat.id
        
        # 创建二级分类
        second_level_categories = {
            "餐饮": ["早餐", "午餐", "晚餐", "下午茶", "夜宵", "奶茶咖啡", "零食", "外卖"],
            "交通": ["高铁", "飞机", "公交", "地铁", "打车", "租车", "加油", "停车"],
            "购物": ["日用品", "服装", "数码", "家居", "美妆", "超市"],
            "居住": ["房租", "水电煤", "物业", "装修", "家具"],
            "娱乐": ["电影", "游戏", "K歌", "旅游", "演出", "健身"],
            "教育": ["学费", "书籍", "课程", "培训", "考试"],
            "医疗": ["药品", "检查", "住院", "保险"],
            "理财": ["投资", "保险", "还款", "转账"],
            "人情": ["红包", "礼物", "请客"],
            "通讯": ["话费", "流量", "宽带"],
            "工作": ["办公", "出差", "兼职"],
            "其他": ["临时", "未知"],
        }
        
        # Emoji映射
        emoji_map = {
            "早餐": "🥪", "午餐": "🍱", "晚餐": "🍲", "下午茶": "☕", "夜宵": "🌙",
            "奶茶咖啡": "🧋", "零食": "🍪", "外卖": "🥡",
            "高铁": "🚄", "飞机": "✈️", "公交": "🚌", "地铁": "🚇", "打车": "🚖",
            "租车": "🚗", "加油": "⛽", "停车": "🅿️",
            "日用品": "🧴", "服装": "👕", "数码": "📱", "家居": "🏠", "美妆": "💄",
            "超市": "🛒",
            "房租": "🏘️", "水电煤": "💡", "物业": "🏢", "装修": "🔧", "家具": "🪑",
            "电影": "🎬", "游戏": "🎮", "K歌": "🎤", "旅游": "✈️", "演出": "🎭", "健身": "💪",
            "学费": "📚", "书籍": "📖", "课程": "📝", "培训": "🎓", "考试": "📋",
            "药品": "💊", "检查": "🩺", "住院": "🏥", "保险": "🛡️",
            "投资": "📈", "保险": "🛡️", "还款": "💳", "转账": "💸",
            "红包": "🧧", "礼物": "🎁", "请客": "🍽️",
            "话费": "📞", "流量": "📶", "宽带": "🌐",
            "办公": "💼", "出差": "✈️", "兼职": "💰",
            "临时": "📌", "未知": "❓",
        }
        
        for parent_name, children in second_level_categories.items():
            parent_key = f"{parent_name}_expense"
            parent_id = category_map.get(parent_key)
            if not parent_id:
                continue
            
            for child_name in children:
                emoji = emoji_map.get(child_name, "📌")
                cat = Category(
                    name=child_name,
                    icon=emoji,
                    type="expense",
                    is_system=True,
                    user_id=None,
                    parent_id=parent_id,
                )
                db.add(cat)
        
        # 收入分类的二级分类
        income_children = ["工资", "奖金", "兼职", "投资", "红包", "其他"]
        income_emoji = {"工资": "💵", "奖金": "🎁", "兼职": "💰", "投资": "📈", "红包": "🧧", "其他": "💵"}
        parent_id = category_map.get("收入_income")
        if parent_id:
            for child_name in income_children:
                emoji = income_emoji.get(child_name, "💵")
                cat = Category(
                    name=child_name,
                    icon=emoji,
                    type="income",
                    is_system=True,
                    user_id=None,
                    parent_id=parent_id,
                )
                db.add(cat)
        
        db.commit()
        print("✅ 默认分类初始化完成")
        print("✅ 默认邀请码: admin123")
        print("✅ 系统配置初始化完成")
        
    except Exception as e:
        db.rollback()
        print(f"❌ 初始化失败: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    init_db()
