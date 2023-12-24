import xlwt

# 关于样式
style_head = xlwt.XFStyle() # 初始化样式

font = xlwt.Font() # 初始化字体相关
font.name = "微软雅黑"
font.bold = True
font.colour_index = 1 # TODO 必须是数字索引

bg = xlwt.Pattern() # 初始背景图案
bg.pattern = xlwt.Pattern.SOLID_PATTERN # May be: NO_PATTERN, SOLID_PATTERN, or 0x00 through 0x12
bg.pattern_fore_colour = 4 # May be: 8 through 63. 0 = Black, 1 = White, 2 = Red, 3 = Green, 4 = Blue, 5 = Yellow, 6 = Magenta, 7 = Cyan, 16 = Maroon, 17 = Dark Green, 18 = Dark Blue, 19 = Dark Yellow , almost brown), 20 = Dark Magenta, 21 = Teal, 22 = Light Gray, 23 = Dark Gray

# 设置字体
style_head.font = font
# 设置背景
style_head.pattern = bg


# 创建一个excel
excel = xlwt.Workbook()
# 添加工作区
sheet = excel.add_sheet("档案")

# 标题信息
head = ["代码"]
for index,value in enumerate(head):
    sheet.write(0,index,value,style_head)

# 内容信息
content = [("张张张"),("嘿嘿嘿")]
for index,value_list in enumerate(content,1):
    for i,value in enumerate(value_list):
        sheet.write(index,i,value)

# 保存excel
excel.save("../Data/MACDpoint")