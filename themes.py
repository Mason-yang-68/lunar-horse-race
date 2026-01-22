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
            {"question": "明昌五金行位於台南哪一區？", "options": ["仁德區", "歸仁區", "關廟區"], "answer": 1},
            {"question": "五金行的「五金」原本是指？", "options": ["金銀銅鐵錫", "鉀鈣鈉鎂鋁", "鋼鐵雷神"], "answer": 0},
            {"question": "在傳統五金行買螺絲怎麼算錢？", "options": ["算顆數", "秤重賣", "看心情"], "answer": 1},
            {"question": "什麼東西越洗越髒？", "options": ["衣服", "水", "盤子"], "answer": 1},
            {"question": "便利商店門自動開是用什麼感應？", "options": ["聲控", "紅外線", "臉部辨識"], "answer": 1},
            {"question": "象棋裡面的「馬」是走什麼步？", "options": ["直走", "日字步", "田字步"], "answer": 1},
            {"question": "鎖螺絲口訣「右旋」通常是？", "options": ["轉鬆", "轉緊", "自爆"], "answer": 1},
            {"question": "藍罐裝除鏽潤滑的神油是？", "options": ["WD-40", "凡士林", "沙拉油"], "answer": 0},
            {"question": "台灣捲尺上常見的單位是公分和？", "options": ["台寸", "光年", "海里"], "answer": 0},
            {"question": "想要把水管鋸斷要用什麼？", "options": ["鐵鎚", "鋸子", "剪刀"], "answer": 1},
            {"question": "牆壁鑽孔後要塞進去的東西叫？", "options": ["這裡癢", "壁虎", "蜥蜴"], "answer": 1},
            {"question": "絕緣膠帶（電火布）最常見顏色？", "options": ["黑色", "粉紅色", "透明"], "answer": 0},
            {"question": "「梅花板手」的開口形狀像？", "options": ["圓形", "六角/十二角", "星星"], "answer": 1},
            {"question": "珍珠奶茶的珍珠是用什麼做的？", "options": ["麵粉", "樹薯粉", "米粉"], "answer": 1},
            {"question": "換燈泡時最重要的第一步是？", "options": ["關電源", "戴墨鏡", "喝口水"], "answer": 0},
            {"question": "歸仁有名的農產除了釋迦還有？", "options": ["菱角", "綠竹筍", "草莓"], "answer": 1},
            {"question": "明昌五金行附近最熱鬧的圓環？", "options": ["歸仁圓環", "東門圓環", "仁愛圓環"], "answer": 0},
            {"question": "哆啦A夢原本是什麼顏色的？", "options": ["藍色", "黃色", "紅色"], "answer": 1},
            {"question": "歸仁的高鐵站正式名稱是？", "options": ["高鐵歸仁站", "高鐵台南站", "高鐵沙崙站"], "answer": 1},
            {"question": "在明昌五金行絕對買不到什麼？", "options": ["螺絲起子", "麥當勞薯條", "水管"], "answer": 1},
            {"question": "哪一種鉗子聽起來最兇？", "options": ["尖嘴鉗", "老虎鉗", "鯉魚鉗"], "answer": 1},
            {"question": "哪一個月有 28 天？", "options": ["二月", "閏年才有", "每個月都有"], "answer": 2},
            {"question": "什麼釘子最難拔？", "options": ["鐵釘", "鋼釘", "眼中釘"], "answer": 2},
            {"question": "什麼桶子永遠裝不滿？", "options": ["水桶", "馬桶", "垃圾桶"], "answer": 1},
            {"question": "章魚總共有幾顆心臟？", "options": ["1顆", "3顆", "8顆"], "answer": 1},
            {"question": "草莓的種子長在哪裡？", "options": ["果肉裡", "表皮上", "葉子上"], "answer": 1},
            {"question": "現在最紅的 AI 是什麼縮寫？", "options": ["愛因斯坦", "人工智慧", "蘋果手機"], "answer": 1},
            {"question": "哪一種動物天生「不會跳」？", "options": ["兔子", "大象", "羚羊"], "answer": 1},
            {"question": "過年吃「長年菜」不能做什麼？", "options": ["咬斷", "加醬油", "吹氣"], "answer": 0},
            {"question": "過年打破碗要馬上說什麼？", "options": ["對不起", "碎碎平安", "舊的不去"], "answer": 1},
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
