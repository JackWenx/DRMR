import json
import utils
import openai
import joblib
import re
from joblib import Parallel, delayed
from itertools import cycle
from utils import *

api_list = [
]
def got_score(text):
    match = re.search(r'\[(\d+)\]', text)
    if match:
        number_str = match.group(1)
        number = int(number_str)
        print("分数是:", number)
    else:
        print("未找到匹配的数字")
        print(text)
        number = -1
    return number

def scoring(data, key):
    openai.api_base = "https://api.aiguoguo199.com/v1"
    openai.api_key = key
    role_name =  data["role"]
    user_name = data["user_role"]
    context = data["context"]
    user_role = data["user_role"]
    model_output = data["model_output"]
#     test_special_relation =  data["对话关系"]

    role_events = find_events(role_name, events, context, 2)

    pers_prompt = []
    mems_prompt = []
    relations_prompt = []
    system_prompt = {"role":"system","content":"你是一个角色间对话打分评估模型,判断模型生成的回答是否符合相关的要求,并给出分数"}

    pers_prompt.append(system_prompt)
    per_prompt = per_system.format(role_name=role_name, role_profile=role_profile, context = context, model_output = model_output)
    pers_prompt.append({"role": "user", "content":per_prompt})
    per_score = got_score(get_response(pers_prompt))
#     print(per_score)

    mems_prompt.append(system_prompt)
    mem_prompt = mem_system.format(role_name=role_name, user_role = user_role, role_profile=role_profile,events = role_events, context = context, model_output = model_output)
    mems_prompt.append({"role": "user", "content":mem_prompt})
    mem_score = got_score(get_response(mems_prompt))
#     print(mem_score)

    relations_prompt.append(system_prompt)
    relation_prompt = general_relation.format(role_name=role_name, user_role=user_role, role_profile=role_profile, model_output = model_output,role_relation = test_general_relation, context = context)
    relations_prompt.append({"role": "user", "content":relation_prompt})
    relation_score = got_score(get_response(relations_prompt))
#     print(relation_score)
    data["个性分数"]=per_score
    data["记忆分数"]=mem_score
    data["关系分数"]=relation_score

    return data

for folder_name in os.listdir("./test/武林外传"):
    if folder_name == "佟湘玉":
        test_novel = "武林外传"
        test_name = folder_name
        # test_name = "郭芙蓉"
        model_name = "RoleGLM"
        events_file = "./test/"+test_novel+"/"+test_name+"/"+test_name+"_bilingual.json"
        test_file = "./test/"+test_novel+"/"+test_name+"/"+test_name+"_"+model_name+"_generate.json"
        profile_file = "./test/"+test_novel+"/"+test_name+"/"+test_name+"_profile.txt"
        relation_file =  "./test/"+test_novel+"/"+test_name+"/"+test_name+"_relation.txt"
        output_file = "./test/"+test_novel+"/"+test_name+"/"+test_name+"_"+model_name+"_evaluate2.json"

        # test_file = "./test/kuangbiao/高启强/高启强_RoleGPT_generate.json"
        # with open('.demo/character_profiles.json','r') as f:
        #     role_informations = json.load(f)

        with open(test_file, 'r',encoding='utf-8') as file:
            datas = json.load(file)

        with open(events_file, 'r',encoding='utf-8') as file:
            data_event = json.load(file)

        with open(profile_file,'r',encoding='utf-8') as file:
            role_profile = file.read()

        with open(relation_file ,'r',encoding='utf-8') as file:
            test_general_relation = file.read()


        events = [entry["context"] for entry in data_event]

        with open("./data/prompt/prompt_test_personality.txt", 'r',encoding='utf-8') as file:
            per_system = file.read()
        with open("./data/prompt/prompt_test_memorization.txt", 'r', encoding='utf-8') as file:
            mem_system = file.read()
        with open("./data/prompt/prompt_test_relationgeneral.txt", 'r', encoding='utf-8') as file:
            general_relation = file.read()


        i = 0
        score = []
        api_cycle = cycle(api_list)
        # results = scoring(datas[0],api_list[0])
        results = Parallel(n_jobs=15)(delayed(scoring)(data,api_now) for data, api_now in zip(datas, api_cycle))

        # print(average_per,average_memorization,average_relation)

        f = open(output_file,'w',encoding='utf-8')
        f.write(json.dumps(results, ensure_ascii=False, indent=4))
        f.flush()
