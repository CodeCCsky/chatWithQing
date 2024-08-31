import yaml

api_key = None
prt = None
name = None
your_sex = None
favourite_food = None
user_location = None

print("初始化中\n根据提示填入你的信息")
print("这些信息将以非加密形式存储在private_setting.yaml中，本项目仅会在调用 deepseek api 的时候传递这些信息，理论上不会造成泄露。")
print("但出于信息安全考虑，对于敏感信息强烈不建议按真实情况填写。具体情况请查看README文件的隐私政策部分。")

api_key = input("你的 api key > ")
name = input("你想让晴小姐叫你什么 > ")
your_sex = input("你的性别(输入 M 或 F , M 为男生, F 为女生) > ")
if your_sex.upper() == 'M':
    your_sex = '男'
elif your_sex.upper() == 'F':
    your_sex = '女'
else:
    print("warning: 你输入了除 M 或 F 以外的字符。这将会直接作为性别信息传递。")
favourite_food = input("你喜欢的食物 > ")
user_location = input("你的地址(*不建议填写真实地址*)\n> ")


with open(r"system_prompt/system_prompt_main.txt",'r',encoding='utf-8') as f:
    prt = f.read()
data = {
    'api_key' : api_key,
    'user_name' : name,
    'user_sex' : your_sex,
    'favourite_food' : favourite_food,
    'user_location' : user_location,
    'system_prompt_main' : prt,
}
try:
    with open(r"setting/private_setting.yaml",'w',encoding='utf-8') as f:
        yaml.dump(data=data,stream=f,allow_unicode=True)
    print("已成功写入")
except Exception as e:
    print(e)