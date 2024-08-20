import yaml

prt = None
prt2 = None
name = None
your_sex = None
favourite_food = None
liked_style = None
user_location = None

with open(r"system_prompt_main_chat.txt",'r',encoding='utf-8') as f:
    prt = f.read()
with open(r"system_prompt_action.txt",'r',encoding='utf-8') as f:
    prt2 = f.read()
data = {
    'api_key' : "***REMOVED***",
    'user_name' : name,
    'user_sex' : your_sex,
    'favourite_food' : favourite_food,
    'liked_style' : liked_style,
    'user_location' : user_location,
    'system_prompt_main_chat' : prt,
    'system_prompt_action' : prt2,
}

with open(r"private_setting.yaml",'w',encoding='utf-8') as f:
    yaml.dump(data=data,stream=f,allow_unicode=True)
