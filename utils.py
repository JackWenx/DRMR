import openai
import os
import requests
import requests
import zhipuai
import numpy as np
import time
import dashscope
from http import HTTPStatus
from zhipuai import ZhipuAI
from openai.embeddings_utils import get_embedding, cosine_similarity

openai.api_base =
openai.api_key =

def get_response_glm3(prompt):
    client = ZhipuAI(api_key=)
    response = client.chat.completions.create(
    model="glm-3-turbo",
    messages= prompt,
    )
    print(response.choices[0].message.content)
    return response.choices[0].message.content

def get_response_qwen(prompt,key):
    dashscope.api_key = key
    response = dashscope.Generation.call(
        'qwen1.5-14b-chat',
        messages=prompt,
        result_format='message',
    )
    if response.status_code == HTTPStatus.OK:
        content = response.output.get("choices", [{}])[0].get("message", {}).get("content", "默认值或错误信息")
        print(content)
    else:
        content = get_response_qwen(prompt,key)
        print(content)
    return content

def find_events(role_name, events, query, k):
    embedding_path = "./test/"+"武林外传"+"/"+role_name+"/"+role_name+".npy"
#     embedding_path = r".\test\kuangbiao\安欣\安欣.npy"
    i = 0
    embedding_query = openai.Embedding.create(input=query, model="text-embedding-ada-002")["data"][0]["embedding"]
    embedding_vectors = []
    if  os.path.exists(embedding_path):
        embedding_vectors = np.load(embedding_path)
    else:
        for event in events:
            emb = openai.Embedding.create(input=event, model="text-embedding-ada-002")["data"][0]["embedding"]
            embedding_vectors.append(emb)
            i = i + 1
            print(i)
        embedding_vectors = np.array(embedding_vectors)
        np.save(embedding_path, embedding_vectors)
    cosine_similarities = cosine_similarity(embedding_vectors, embedding_query)
    top_k_indices = np.argsort(cosine_similarities.flatten())[::-1][:k]
    top_k_events = [events[i] for i in top_k_indices]
    return top_k_events


def find_events_relation(events, history, role_name, user_name, k):

    embedding_path = "./test/"+"武林外传"+"/"+role_name+"/"+role_name+".npy"

    embedding_history = openai.Embedding.create(input=history, model="text-embedding-ada-002")["data"][0]["embedding"]

    embedding_user = openai.Embedding.create(input=user_name, model="text-embedding-ada-002")["data"][0]["embedding"]

    embedding_vectors = []
    if  os.path.exists(embedding_path):
        embedding_vectors = np.load(embedding_path)
    else:
        for event in events:
            emb = openai.Embedding.create(input=event, model="text-embedding-ada-002")["data"][0]["embedding"]
            embedding_vectors.append(emb)
        embedding_vectors = np.array(embedding_vectors)
        np.save(embedding_path, embedding_vectors)
    cosine_similarities = cosine_similarity(embedding_vectors, embedding_history) + cosine_similarity(embedding_vectors, embedding_user)
    top_k_indices = np.argsort(cosine_similarities.flatten())[::-1][1:k+1]
    top_k_events = [events[i] for i in top_k_indices]
    concatenated_string = ''.join(top_k_events)
    result = concatenated_string[:3000]
    return result


def read_events(folder_path):
    stories = []
    for filename in os.listdir(folder_path):
        if filename.endswith(".txt"):
            file_path = os.path.join(folder_path, filename)
            with open(file_path, 'r', encoding='utf-8') as file:
                story = file.read()
                stories.append(story)
    return stories

def calculate_similarity(text1, text2):


    emb1 = openai.Embedding.create(input=text1, model="text-embedding-ada-002")["data"][0]["embedding"]
    emb2 = openai.Embedding.create(input=text2, model="text-embedding-ada-002")["data"][0]["embedding"]
    similarity_score = cosine_similarity(emb1, emb2)

    return similarity_score


def get_response(prompt):
    out = ''
    try:
        response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo-0125",
                messages=prompt,
                max_tokens=1024,
                stream = True
        )
    except Exception as e:
        print(prompt)
        return out
    for i in response:
        try:
            out += i['choices'][0]['delta']['content']
        except Exception as e:
            break
    return out

# def get_response(prompt):
#     response = openai.ChatCompletion.create(
#         model="gpt-3.5-turbo",
#         messages=prompt,
#         max_tokens=300
#     )
#     return response['choices'][0]['message']['content'].strip()

def sorted_events(stories, user_role, role_special, role_name):
    sorted_stories = sorted(stories, key=lambda story: sum([
        calculate_similarity(story, user_role),
        calculate_similarity(story, role_special),
        calculate_similarity(story, role_name)
    ]), reverse=True)

    print("Sorted Stories:")
    for i, text in enumerate(sorted_stories, start=1):
        print(f"{i}. {text}")
    return sorted_stories

def sorted_events_q(character_stories, query, K):
    sorted_stories = sorted(stories, key=lambda story: calculate_similarity(story, query), reverse=True)
#         print("Sorted Stories:")
#     for i, text in enumerate(sorted_stories, start=1):
#         print(f"{i}. {text}")
    return sorted_stories

def update_talk_history(talk_history, query,answer,user_name,role_name):
    dialogue_fragment = f"{user_name}:「{query}」\n{role_name}:「{answer}」"
    talk_history.append(dialogue_fragment)
    return talk_history


