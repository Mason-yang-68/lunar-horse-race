# Theme configurations for the horse racing game
# Each theme has: name, background, questions

THEMES = {
    'hashimae': {
        'id': 'hashimae',
        'name': '橋前駅版',
        'background': None,  # Use default CSS gradient
        'questions': [
            {"question": "馬年是十二生肖的第幾位？", "options": ["第六位", "第七位", "第八位"], "answer": 1},
            {"question": "世界上速度最快的馬是？", "options": ["純血馬", "阿拉伯馬", "蒙古馬"], "answer": 0},
            {"question": "馬的壽命通常是幾年？", "options": ["10-15年", "25-30年", "40-50年"], "answer": 1},
            {"question": "馬睡覺時通常是什麼姿勢？", "options": ["躺著", "站著", "坐著"], "answer": 1},
            {"question": "一匹成年馬大約有幾顆牙齒？", "options": ["20顆", "40顆", "60顆"], "answer": 1},
            {"question": "過年發紅包代表什麼？", "options": ["祝福", "炫富", "習慣"], "answer": 0},
            {"question": "新年的「年」原本指什麼？", "options": ["季節", "怪獸", "神明"], "answer": 1},
            {"question": "台灣過年必吃的「長年菜」是？", "options": ["芥菜", "高麗菜", "大白菜"], "answer": 0},
            {"question": "發紅包時說「恭喜發財」對方會說？", "options": ["謝謝", "紅包拿來", "大吉大利"], "answer": 1},
            {"question": "過年時貼春聯要從哪邊開始貼？", "options": ["左邊", "右邊", "都可以"], "answer": 1},
        ]
    },
    'mingchang': {
        'id': 'mingchang',
        'name': '明昌五金行版',
        'background': '/static/images/mingchang_bg.jpg',
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
