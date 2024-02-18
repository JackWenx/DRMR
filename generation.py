import openai
import re
from utils import *


def got_answer(text):
    match = re.search(r'<([^>]*)>', text)
    if match:
        corrected_dialogue = match.group(1)
        print(corrected_dialogue)
    else:
        return 0


def update_role_memory(events,role_memory):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo-0125",
        message=[{"role":"system","content":"Extract events"},
                {"role":"user","content":f"{events}"}],
        max_tokens=400
    )
    events_extract = response['choices'][0]['message']['content'].strip()
    role_memory = f"{role_memory} {' '.join(events_extract)}"
    print(role_memory)
    return role_memory

def judge_answer(query, answer, user_name, role_name, role_memory):
    system_prompt = f"你是一位导演，而 {role_name} 的设定是 {role_memory}。请在按照下面评分步骤和示例给出评分,评分按照['score':number]的格式输出"
    prompt = f'''{user_name}问{role_name}：{query}，而{role_name}的回答是：{answer}。{role_name}的设定和主观态度是{role_memory}。请评估回答 {answer} 在与{role_name}的设定相符方面的程度。
    给出一个1到5的评分。0表示回答与设定相反，5表示回答与设定相符。
    解释原因后并给出评分，评分请输出['score':number]的输出格式。
    接下来，我将为您提供3个输出示例。它们的主要目的是帮助您了解输出格式和事实性定义。\n
    [输出示例]\n
    猪八戒喜欢吃，但其回答是“我根本不吃”,不符合猪八戒贪吃的设定。因此评分为：['score':1]\n
    小明喜欢运动，但回答是“我通常不运动”，不符合小明喜欢运动的设定。因此评分为：['score':1]\n
    超级小桀喜欢玩游戏，回答是“我是超级马里奥的忠实粉丝”，和游戏迷的设定非常相符。因此评分为：['score':5]\n'''

#     print(system_prompt)
#     print(prompt)

    conversation_history = [
        {"role": "system", "content":f"{system_prompt}"},
        {"role": "user", "content": f"{prompt}"}]
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo-0125",
        messages=conversation_history,
        temperature=0.1,
        max_tokens=300
    )

    judge = response['choices'][0]['message']['content'].strip()
    match = re.search(r"'score':(\d+)", judge)
    if match:
        score = int(match.group(1))
        print("Extracted Score:", score)
    else:
        score = 5
        print(judge)
        print("No match found for 'score'")
    return score


def refine(answer, query ,events, user_name, role_name, role_memory):
    system_prompt = f'''你将扮演{role_name} 回答 {user_name} 的问题。你的初步回答："{answer}" 不够准确或详细。根据 {role_name} 的背景和与 {user_name} 相关的关键事件，进行必要的修正，并在最后以特殊标记<>清晰地标示出修正后的对话。
{user_name} 向 {role_name} 提出的询问是：“{query}”，你需要根据 {role_name} 的经历和以下最相关事件修正原先的回答：保持上下文通顺，注意只输出你视角的回答,而不需要其他内容'''
    with open("./data/prompt/refine.txt", 'r',encoding='utf-8') as file:
        refine_prompt = file.read()
    prompt = refine_prompt.format(role_memory=role_memory, events = events, role_name = role_name, user_name = user_name)

#     print(system_prompt)
#     print(prompt)

    conversation_history = [
        {"role": "system", "content": f"{system_prompt}"},
        {"role": "user", "content": f"{prompt}"}]
#     print(conversation_history)
    response = openai.ChatCompletion.create(
        model = "gpt-3.5-turbo-0125",
        messages = conversation_history
#         max_tokens=400
    )
    answer_refine = response['choices'][0]['message']['content'].strip()
    print(answer_refine)
    answer_refined = got_answer(answer)
    if answer_refined == 0:
        return answer
    else:
        return answer_refined
