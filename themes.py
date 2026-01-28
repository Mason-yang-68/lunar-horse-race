# Theme configurations for the horse racing game
# Each theme has: name, track_background (for oval track), questions

THEMES = {
    'hashimae': {
        'id': 'hashimae',
        'name': '橋前駅版',
        'track_background': None,  # Use default track style
        'questions': [
            {"question": "在橋前駅店裡...招牌鬆餅咬開是？", "options": ["湯圓", "麻糬", "棉花糖"], "answer": 1},
            {"question": "在橋前駅店裡...外牆那隻貓去哪？", "options": ["釣魚", "太空", "飆車"], "answer": 1},
            {"question": "在橋前駅店裡...戶外塑木板上停什麼車？", "options": ["跑車", "老機車", "戰車"], "answer": 1},
            {"question": "在橋前駅店裡...廁所牆壁滿滿是？", "options": ["鏡子", "手繪圖案", "磁磚"], "answer": 1},
            {"question": "在橋前駅店裡...是什麼搭建起來的？", "options": ["水泥", "貨櫃屋", "厚紙版"], "answer": 1},
            {"question": "在橋前駅店裡...帶寵物進室內要？", "options": ["綁繩子", "放提籃或推車內", "穿衣服"], "answer": 1},
            {"question": "在橋前駅店裡...用餐限時幾分鐘？", "options": ["90分", "120分", "無限時"], "answer": 1},
            {"question": "在橋前駅店裡...每週哪一天公休？", "options": ["週一", "週二", "週三"], "answer": 1},
            {"question": "在橋前駅店裡...招牌鬆餅形狀是？", "options": ["圓形", "方形", "愛心"], "answer": 2},
            {"question": "在橋前駅店裡...口袋麵包夾什麼？", "options": ["打拋豬(莎味迪卡口味)", "咖哩雞", "牛肉片"], "answer": 0},
            {"question": "在橋前駅店裡...燻雞可頌搭配？", "options": ["薯泥", "生菜沙拉", "白飯"], "answer": 1},
            {"question": "在橋前駅店裡...每人低消要點？", "options": ["一顆愛心品項", "一份鬆餅", "200元"], "answer": 0},
            {"question": "在橋前駅店裡...WiFi 密碼通常是？", "options": ["老闆生日", "店名加地址號碼", "12345678"], "answer": 1},
            {"question": "在橋前駅店裡...點餐結帳要去？", "options": ["廚房", "櫃台", "等店員來"], "answer": 1},
            {"question": "在橋前駅店裡...店在南雄路幾段？", "options": ["一段", "二段", "三段"], "answer": 1},
            {"question": "在橋前駅店裡...戶外用餐區鋪？", "options": ["紅磚", "綠草皮或塑木板", "水泥"], "answer": 1},
            {"question": "在橋前駅店裡...整間店走什麼風？", "options": ["日式風", "工業風", "宮廷風"], "answer": 1},
            {"question": "在橋前駅店裡...畫完單要去？", "options": ["櫃台結帳", "廚房大叫", "丟在桌上"], "answer": 0},
            {"question": "在橋前駅店裡...水要？", "options": ["自己拿", "大喊店員", "變魔術"], "answer": 0},
            {"question": "在橋前駅店裡...絕對不能帶？", "options": ["外食", "錢包", "手機"], "answer": 0},
            {"question": "在橋前駅店裡...鬆餅現烤要？", "options": ["等一下", "馬上有", "昨天做"], "answer": 0},
            {"question": "在橋前駅店裡...櫃台收什麼？", "options": ["現金", "支票", "欠條"], "answer": 0},
            {"question": "在橋前駅店裡...冰沙上面有？", "options": ["薄荷葉", "鹹菜", "荷包蛋"], "answer": 0},
            {"question": "在橋前駅店裡...熱拿鐵表面？", "options": ["有拉花", "黑黑的", "有蒼蠅"], "answer": 0},
            {"question": "在橋前駅店裡...鬆餅旁那是？", "options": ["冰淇淋", "哇沙米", "醬油膏"], "answer": 0},
            {"question": "在橋前駅店裡...店內燈光是？", "options": ["溫馨黃光", "手術燈白", "七彩霓虹"], "answer": 0},
            {"question": "在橋前駅店裡...戶外區可以看到？", "options": ["許縣溪/風景", "垃圾場", "火山爆發"], "answer": 0},
        ]
    },
    'mingchang': {
        'id': 'mingchang',
        'name': '明昌五金行版',
        'track_background': '/static/images/mingchang_track.jpg',  # Custom track image
        'avatar_folder': 'mingchang',  # Subfolder in static/images/
        'avatar_prefix': 'hw_horse',   # Prefix for horse images (hw_horse1.png, etc.)
        'questions': [
            {"question": "明昌五金行在哪一區？", "options": ["仁德區", "歸仁區", "關廟區"], "answer": 1},
            {"question": "五金的「五金」原意？", "options": ["金銀銅鐵錫", "鉀鈣鈉鎂鋁", "鋼鐵雷神"], "answer": 0},
            {"question": "傳統五金行螺絲怎麼賣？", "options": ["算顆數", "秤重賣", "看心情"], "answer": 1},
            {"question": "鎖螺絲「右旋」是？", "options": ["轉鬆", "轉緊", "自爆"], "answer": 1},
            {"question": "藍罐潤滑神油是？", "options": ["WD-40", "凡士林", "沙拉油"], "answer": 0},
            {"question": "台灣捲尺常見單位？", "options": ["公分/台寸", "公分/光年", "公分/海里"], "answer": 0},
            {"question": "鋸水管要用大剪刀還是？", "options": ["鐵鎚", "鋸子", "指甲剪"], "answer": 1},
            {"question": "鑽牆後塞進去的是？", "options": ["鼻屎", "壁虎", "蜥蜴"], "answer": 1},
            {"question": "電火布常見顏色？", "options": ["黑色", "粉紅色", "透明"], "answer": 0},
            {"question": "梅花板手開口像？", "options": ["圓形", "星星", "愛心"], "answer": 1},
            {"question": "換燈泡第一步？", "options": ["關電源", "戴墨鏡", "喝口水"], "answer": 0},
            {"question": "明昌附近最熱鬧圓環？", "options": ["歸仁圓環", "東門圓環", "仁愛圓環"], "answer": 0},
            {"question": "明昌絕對買不到？", "options": ["螺絲起子", "麥當勞薯條", "水管"], "answer": 1},
            {"question": "聽起來最兇的鉗子？", "options": ["尖嘴鉗", "老虎鉗", "鯉魚鉗"], "answer": 1},
            {"question": "什麼釘子最難拔？", "options": ["鐵釘", "鋼釘", "眼中釘"], "answer": 2},
            {"question": "什麼桶子永遠裝不滿？", "options": ["水桶", "馬桶", "垃圾桶"], "answer": 1},
            {"question": "黏住不聽話的嘴巴用？", "options": ["強力快乾膠", "口紅膠", "雙面膠"], "answer": 0},
            {"question": "活動板手的特技？", "options": ["調整開口", "跳舞", "變身"], "answer": 0},
            {"question": "鑽牆鑽到水管會？", "options": ["噴水", "噴錢", "噴石油"], "answer": 0},
            {"question": "買油漆老闆通常問？", "options": ["水性還油性", "加辣嗎", "喝溫的"], "answer": 0},
            {"question": "門會叫要噴什麼？", "options": ["潤滑油", "殺蟲劑", "辣椒水"], "answer": 0},
            {"question": "量腰圍通常用？", "options": ["捲尺", "地尺", "溫度計"], "answer": 0},
            {"question": "延長線插太多會？", "options": ["跳電", "省電", "發財"], "answer": 0},
            {"question": "綁東西最快的是？", "options": ["束線帶", "橡皮筋", "鞋帶"], "answer": 0},
            {"question": "捲尺收回要小心？", "options": ["割手", "咬人", "爆炸"], "answer": 0},
            {"question": "門把壞了要買？", "options": ["喇叭鎖", "密碼鎖", "機車鎖"], "answer": 0},
            {"question": "水性漆滴到地板用？", "options": ["濕抹布", "砂紙", "衛生紙"], "answer": 0},
            {"question": "這裡面誰不賣五金？", "options": ["麥當勞", "明昌", "小北"], "answer": 0},
            {"question": "矽利康是用來？", "options": ["防水填縫", "刷牙", "洗臉"], "answer": 0},
            {"question": "熱熔膠要搭配？", "options": ["熱熔槍", "吹風機", "打火機"], "answer": 0},
        ]
    }
}

# Default theme
DEFAULT_THEME = 'hashimae'

def get_theme(theme_id):
    """Get theme configuration by ID"""
    return THEMES.get(theme_id, THEMES[DEFAULT_THEME])

def get_questions(theme_id):
    """Get questions for a theme"""
    theme = get_theme(theme_id)
    return theme['questions']

def get_all_themes():
    """Get list of all available themes"""
    return [{'id': t['id'], 'name': t['name']} for t in THEMES.values()]
