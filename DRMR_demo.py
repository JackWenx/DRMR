import json
import utils
import openai
import joblib
from joblib import Parallel, delayed
from itertools import cycle
# from memory_build import *
from util_qwen import *
from relationmap import *
# from generation import *
# from memory_build import *



def concat_messages(conversations, role, system):
    history = []
    first_query = system
    if conversations[0]['from'] == role: #判断截取的对话段,第一个是否来自于原对话,对于开始做一个开头
        first_response = f"好的！现在我来扮演{role}。" + "我首先发话：" + conversations[0]['value']
    else:
        first_response = f"好的！现在我来扮演{role}。"

    history.append({"role": "user", "content": first_query}) #"user"替换成对应角色,对应chatgpt的对话历史
    history.append({"role": "assistant", "content": first_response})

    for i in range(len(conversations)):
        if conversations[i]['from'] == role:
            if i ==0: # 0已经被特殊处理
                continue
            else:
                assert conversations[i-1]['from'] != role
                query = f"{conversations[i-1]['from']}：" + conversations[i-1]['value'] #构成对话方的提问
                response = f"{conversations[i]['from']}：" + conversations[i]['value'] #构成角色方的回答
            history.append({"role": "user", "content": query})
            history.append({"role": "assistant", "content": response})
    assert conversations[-1]['from'] != role

    query = f"{conversations[-1]['from']}：" + conversations[-1]['value'] #选取角色最后一个问题做检测标准
    return history, query

def make_inputs(context):
    dialogues= context.split('\n')
    inputs = []
    for dial in dialogues:
        role = dial.split("：")[0]
        dial = "：".join(dial.split("：")[1:])
        inputs.append({"from":role,"value":dial}) #按照'\n'将语句划分开,分成很多轮次的对话
    return inputs

def get_response_RoleRelation(data, events, key, key_q):
    openai.api_base = "https://api.aiguoguo199.com/v1"
    openai.api_key = key
    dashscope.api_key = key_q
    context = data['context']
    role_name = data['role']
    user_name = data['user_role']
#     role_profile = role_informations[role]
    role_start = f'''现在请你扮演一个角色扮演专家。请你扮演{role_name}进行对话。只一问一答，不扮演别的角色'''

    messages,query = concat_messages(make_inputs(context), role_name, role_start)

    events_clique = find_relation_events_clique(events, messages)

    events_base = find_events_relation(events_clique, context, role_name, user_name, 3)

    role_relation = generate_relation(user_name, role_name, role_profile, events_base)
#     role_relation = []
#     print(role_relation)
    role_memory = generate_role_memory(user_name, role_name, role_profile, role_relation)
    print(role_memory)
    with open("./data/prompt/RoleRelation_system.txt", 'r',encoding='utf-8') as file:
        role_system = file.read()

    system_prompt = role_system.format(role_name=role_name, role_memory=role_memory, user_name = user_name)
    conversation_history=[]
    conversation_history.append({"role": "system", "content": system_prompt})
    conversation_history = conversation_history + messages
    conversation_history.append({"role": "user","content": query})

#     print(conversation_history)
    answer = get_response_qwen(conversation_history)
    print("初步回答：",answer)

    if judge_answer(query, answer, user_name, role_name, role_memory) <= 4:
        print("________________________")
        events_query = find_events(role_name,script_events, query, 2)
        answer = refine(answer, query, events_query, user_name, role_name, role_memory)

    print(answer)
    data["model_output"]=answer
#     print(data["model_output"])
#     score = role_evaluate(role_name,role_profile,messages,query+"\n"+data["model_output"])
#     print(score)
    return data
#
api_cycle = cycle(api_list)
api2_cycle = cycle(api2_list)
for folder_name in os.listdir("./test/武林外传"):
    test_novel = "武林外传"
    test_name = folder_name
    model_name =
    test_file = "./test/"+test_novel+"/"+test_name+"/"+test_name+"_bilingual.json"
    profile_file = "./test/"+test_novel+"/"+test_name+"/"+test_name+"_profile.txt"
    output_file = "./test/"+test_novel+"/"+test_name+"/"+test_name+"_"+model_name+"_generate.json"

    with open(test_file,'r',encoding='utf-8') as f:
        datas = json.load(f)

    with open(test_file,'r',encoding='utf-8') as f:
        script_datas = json.load(f)

    with open(profile_file, 'r',encoding='utf-8') as file:
         role_profile = file.read()

    role_events = [entry["context"] for entry in datas]
    script_events = [entry["context"] for entry in script_datas]

    i = 0
    results = []
    for entry in datas:
        if entry['id'] == 6328:
            results = get_response_RoleRelation(entry,role_events,api_list[0],api2_list[0])
#         results = Parallel(n_jobs=3)(delayed(get_response_RoleRelation)(data,role_events,api_now,api_q) for data, api_now,api_q in zip(datas, api_cycle, api2_cycle))
    f = open(output_file,'w',encoding="utf-8")
    f.write(json.dumps(results, ensure_ascii=False, indent=4))
    f.flush()
