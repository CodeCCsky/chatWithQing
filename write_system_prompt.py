import yaml

prt = None
name = '***REMOVED***'
your_sex = '***REMOVED***'
favourite_food = '***REMOVED***'
liked_style = '***REMOVED***'
user_location = '***REMOVED***'

with open(r"system_prompt_main.txt",'r',encoding='utf-8') as f:
    prt = f.read()
data = {
    'api_key' : "***REMOVED***",
    'user_name' : name,
    'user_sex' : your_sex,
    'favourite_food' : favourite_food,
    'liked_style' : liked_style,
    'user_location' : user_location,
    'system_prompt_main' : prt,
}

with open(r"private_setting.yaml",'w',encoding='utf-8') as f:
    yaml.dump(data=data,stream=f,allow_unicode=True)
