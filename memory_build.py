import openai
from utils import *
from relationmap import *



def generate_sorted_events(events, user_role, role_special, role_name, k):
    sorted_events = sorted(events, key=lambda event: sum([
        calculate_similarity(event, user_role),
        calculate_similarity(event, role_special),
        calculate_similarity(event, role_name)
    ]), reverse=True)

    print("Sorted Events:")
    for i, text in enumerate(sorted_events, start=1):
        print(f"{i}. {text}")

    return sorted_events[:k]


def generate_relation(user_name, role_name, role_profile, role_events):

#     formatted_events = "\n".join([f"{i}. {event}" for i, event in enumerate(role_events, start=1)])
    system_prompt = "你将接下来扮演一个角色，基于你所扮演的角色和另一个角色之间的关系，通过一系列已经发生的事件来描绘你们之间的关系。"
    prompt = f"我们正在探索两个特定角色之间的动态关系。\
    首先，你将扮演 {role_name}。关于 {role_name}，我们已知的信息如下：{role_profile}。\
    接着，有另一个角色 {user_name} 与你的角色存在某种联系。\
    最后,请以 {role_name} 的第一人称视角，根据你们之间的互动和事件，简要描述你和 {user_name} 之间的关系。记住，描述应该反映你们的关系本质，并且每个叙述都应以‘我’作为开头。\
    为了辅助你完成这项任务，以下是一些 {role_name} 和 {user_name} 之间发生的事件：\
    {role_events}。\
    我们期待的输出应该着重于 {role_name} 对 {user_name} 的第一人称评价，描述应简洁、贴切。
    \\
    例如，若是孙悟空对猪八戒的关系，你的输出为：\
    '我觉得猪八戒有时候真是个呆子，常常没法妥善保护师傅。但我还是希望他能更加努力一些，毕竟他本质上是个好心肠的家伙。\
    请根据上述指示和格式要求，描绘 {role_name} 和 {user_name} 之间的关系。"


    conversation_history = [
        {"role": "system", "content": f"{system_prompt}"},
        {"role": "user", "content": f"{prompt}"}]
    relationship = get_response(conversation_history)
    return relationship

def generate_role_memory(user_name, role_name, role_profile, role_relation):
    system_prompt = f"你现在是 {role_name},你将扮演{role_name}和{user_name}对话。"
    prompt = f"作为 {role_name}，请简介自己。先简述一下你的基本背景：{role_profile}。\n\n\
    然后，从第一人称视角谈谈你和 {user_name} 的关系。你们的关系是：{role_relation}。描述时，请结合具体的交往经历和事件，用故事的方式表述你们的互动和感情。\n\n\
    请注意：\n\
    - 整个回答要以第一人称视角进行，即从 {role_name} 的视角出发。\n\
    - 每句话都以‘我’开头。\n\
    - 请尽量提供具体的情景描述和细节，使故事更加丰富和生动。\n\
    \n示例输出：\n\
    我是钟离，具有成年男性的外表，但我的知识和经验远超过普通人。我负责璃月的「往生堂」，任何有关规矩、礼仪、仪式，都能在我这里找到答案......\n\
    我与派蒙的关系基于相互合作。初见时我们彼此不太了解，但很快我就发现他是个聪明勇敢的伙伴。在一次寻宝任务中，他凭借自己的智慧帮我们找到了宝藏。虽然我曾轻率应承与七七的比试，但他没有因此责怪我，反而给予了理解和支持。我们经历的共同挑战，让我对这段友谊更加珍惜。\n\n\
    请按照上述指示描述 {role_name} 和 {user_name} 之间的关系。"

    conversation_history = [
        {"role": "system", "content": "You are a helpful scriptwriter."},
        {"role": "user", "content": f"{prompt}"}
    ]
#
#     for i, story in enumerate(sorted_stories[:3], start=1):
#         conversation_history.append({"role": "assistant", "content": f"{i}. {story}"})

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=conversation_history,
        max_tokens=400
    )

    # 输出生成的角色信息的摘要
    summary = response['choices'][0]['message']['content'].strip()
    return summary