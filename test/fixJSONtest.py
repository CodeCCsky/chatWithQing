import sys
import os

current_file_path = os.path.abspath(__file__)
parent_dir = os.path.dirname(current_file_path)
grandparent_dir = os.path.dirname(parent_dir)
os.chdir(grandparent_dir)
sys.path.insert(0, grandparent_dir)

from third_party.FixJSON import fixJSONwithLLM

err_json = "{\"role_thoughts\": \"这是测试哦\"}\n{\"role_response\": \"测试1213123\"}"

key = ""

print(fixJSONwithLLM.loads(err_json,key))