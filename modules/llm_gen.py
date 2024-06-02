import os
import requests
import json
import time
import ast
import re

import time
import jwt
from dotenv import load_dotenv
load_dotenv()


class LLM_Gen():



    def remove_first_line(self, test_string):
        if test_string.startswith("Here") and test_string.split("\n")[0].strip().endswith(":"):
            return re.sub(r'^.*\n', '', test_string, count=1)
        return test_string
    

    def generate_glm_token(self, apikey: str, exp_seconds: int):
        try:
            id, secret = apikey.split(".")
        except Exception as e:
            raise Exception("invalid apikey", e)

        payload = {
            "api_key": id,
            "exp": int(round(time.time() * 1000)) + exp_seconds * 1000,
            "timestamp": int(round(time.time() * 1000)),
        }

        return jwt.encode(
            payload,
            secret,
            algorithm="HS256",
            headers={"alg": "HS256", "sign_type": "SIGN"},
        )
    
    def gen_baidu_key(self):
        client_ID=os.environ.get('BAIDU_Client_ID')
        client_Secret=os.environ.get('BAIDU_Client_Secret')
        url = "https://aip.baidubce.com/oauth/2.0/token?grant_type=client_credentials&client_id=" + client_ID + "&client_secret=" + client_Secret
    
        payload = ""
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
    
        response = requests.request("POST", url, headers=headers, data=payload)
    
        return response.json().get("access_token")
    

    def generate_text(self, model, prompt, max_tokens):
        
        match model:
            case "glm":
                key=os.environ.get('GLM_API_KEY')
                key=self.generate_glm_token(key,1682503829130)   
                ZHIPU_API_KEY="Bearer "+str(key)
                #return self.generate_glm_text(prompt, model="glm-4",max_tokens=max_tokens, key=ZHIPU_API_KEY)
                return self.generate_glm_text(prompt, model="glm-3-turbo",max_tokens=max_tokens, key=ZHIPU_API_KEY)
            case "ernie":
                key=self.gen_baidu_key()
                return self.generate_baidu_text(prompt, gkey=key)
            case "moonshot":
                key=os.environ.get('KIMI_API_KEY')
                return self.generate_moon_text(prompt, model="moonshot-v1-128k", max_tokens=max_tokens, temperature=0.3,mkey=key)
            case "qwen":
                key=os.environ.get('QWEN_API_KEY')
                return self.generate_qwen_text(prompt, model="qwen-max-longcontext", max_tokens=max_tokens,temperature=0.3,qkey=key)
            case "groq":
                key=os.environ.get('GROQ_API_KEY')
                return self.generate_groq_text(prompt, model="llama3-70b-8192",temperature=0.3,max_tokens=max_tokens,gkey=key)
            case "ollama":
                return self.generate_ollama_text(prompt, model="llama3", max_tokens=max_tokens)
            case "mlx":
                return self.generate_mlx_text(prompt, temperature=0.3, max_tokens=max_tokens)
            case "openrouter":
                key=os.environ.get('OPENROUTER_API_KEY')
                return self.generate_openrouter_text(prompt, model="anthropic/claude-2.1", max_tokens=max_tokens, rkey=key)
            case "openai":
                key=os.environ.get('OPENAI_API_KEY')
                return self.generate_openai_text(prompt, model="gpt-4", max_tokens=max_tokens, zkey=key)
            case "deepseek":
                key=os.environ.get('DEEPSEEK_API_KEY')
                return self.generate_deepseek_text(prompt, model="deepseek-chat", max_tokens=max_tokens, dkey=key)

    def generate_glm_text(self, prompt, model, max_tokens, key):
        headers = {
            "Authorization": key, 
            "Content-Type": "application/json"
        }
        data = {
            "model": model,
            "max_tokens": max_tokens,
            "messages": [
                {"role": "user", "content": prompt}
                ],
        }
        response = requests.post("https://open.bigmodel.cn/api/paas/v4/chat/completions", headers=headers, json=data)
   
        try:
            response_text = response.json()['choices'][0]['message']['content']
        except Exception as e:
            print(f"Error parsing initial queries: {e}")
            print(response.json())
 
        return self.remove_first_line(response_text.strip())

    def generate_baidu_text(self,prompt,gkey):

        url = "https://aip.baidubce.com/rpc/2.0/ai_custom/v1/wenxinworkshop/chat/ernie-speed-128k?access_token=" + gkey
        headers = {
            "Content-Type": "application/json",
        }
        data = {
                "messages":[      
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
        
        }
        response = requests.post(url, headers=headers, json=data)
        #print(response.json())
        try:
            result=response.json().get("result")
        except Exception as e:
            print(f"Error parsing initial queries: {e}")
            print(response.json())

        return self.remove_first_line(str(result).strip())

    def generate_moon_text(self, prompt, model, max_tokens, temperature, mkey):
        headers = {
            "Content-Type": "application/json",
            "Authorization": mkey 
        }
        data = {
            "model": model,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "messages": [
                {"role": "system", "content": "You are a world-class researcher. Analyze the given information and generate a well-structured report."},
                {"role": "user", "content": prompt}
                ],
        }
        response = requests.post("https://api.moonshot.cn/v1/chat/completions", headers=headers, json=data)
        #print(response.json())
        try:
            response_text = response.json()['choices'][0]['message']['content']
        except Exception as e:
            print(f"Error parsing initial queries: {e}")
            print(response.json())
        return self.remove_first_line(response_text.strip())

    def generate_qwen_text(self, prompt, model, max_tokens,temperature,qkey):
        headers = {
            "Content-Type": "application/json",
            "Authorization": qkey 
        }
        data = {
            "model": model,
            "input":{
                "messages":[      
                    {
                        "role": "system",
                        "content": "You are a helpful assistant."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            },
            "parameters": {
                "result_format": "message"
            },
        }
        response = requests.post("https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation", headers=headers, json=data)
    
        try:
            response_text = response.json()['output']['choices'][0]['message']['content']
        except Exception as e:
            print(f"Error parsing initial queries: {e}")
            print(response.json())
        return self.remove_first_line(response_text.strip())

    def generate_groq_text(self, prompt, model, temperature, max_tokens,gkey):
        headers = {
            "Content-Type": "application/json",
            "Authorization": gkey
        }
        data = {
            "model": model,
        
            "messages":[      
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            }
    
        response = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=data)
        try:
            response_text = response.json()['choices'][0]['message']['content']
        except Exception as e:
            print(f"Error parsing initial queries: {e}")
            print(response.json())

        return self.remove_first_line(response_text.strip())
    
    def generate_ollama_text(self, prompt, model="llama3", max_tokens=1000):
        headers = {
            "Content-Type": "application/json",
        }
        data = {
            "model": model,
            "messages": [
                {
                    "role": "system",
                    "content": "You are a helpful assistant."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "max_tokens":max_tokens
        }
        response = requests.post("http://localhost:11434/v1/chat/completions", headers=headers, json=data)
        try:
            response_text = response.json()['choices'][0]['message']['content']
        except Exception as e:
            print(f"Error parsing initial queries: {e}")
            print(response.json())

        return self.remove_first_line(response_text.strip())
    
    def generate_mlx_text(self, prompt, temperature=0.3, max_tokens=1000):
        headers = {
            "Content-Type": "application/json",
        }
        data = {
            "messages": [
                {
                    "role": "system",
                    "content": "You are a helpful assistant."
                },
                {
                    "role": "user",
                    "content": prompt
                },
            ],
            "temperature": temperature,
            "max_tokens":max_tokens
        
        }
        response = requests.post("http://localhost:8081/v1/chat/completions", headers=headers, json=data)
        try:
            response_text = response.json()['choices'][0]['message']['content']
        except Exception as e:
            print(f"Error parsing initial queries: {e}")
            print(response.json())
            
        return self.remove_first_line(response_text.strip())
    
    def generate_openrouter_text(self, prompt, model, max_tokens,rkey):

        headers = {
            "Content-Type": "application/json",
            "Authorization": rkey
        }
        data = {
            "model": model,
            "messages": [
                {
                    "role": "system",
                    "content": "You are a helpful assistant."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "max_tokens":max_tokens
        }
        response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=data)
        #print(response.json())
        try:
            response_text = response.json()['choices'][0]['message']['content']
        except Exception as e:
            print(f"Error parsing initial queries: {e}")
            print(response.json())
            
        return self.remove_first_line(response_text.strip())
    
    def generate_openai_text(self, prompt, model, max_tokens, zkey):
        headers = {
            "Content-Type": "application/json",
            "Authorization": zkey
        }
        data = {
            "model": model,
            "messages": [
                {
                    "role": "system",
                    "content": "You are a helpful assistant."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "max_tokens":max_tokens
        }
        base=os.environ.get('OPENAI_BASE_URL')
        response = requests.post(base, headers=headers, json=data)
        #print(response.json())
        try:
            response_text = response.json()['choices'][0]['message']['content']
        except Exception as e:
            print(f"Error parsing initial queries: {e}")
            print(response.json())
            
        return self.remove_first_line(response_text.strip())
    
    def generate_deepseek_text(self, prompt, model, max_tokens, dkey):
        headers = {
            "Content-Type": "application/json",
            "Authorization": dkey
        }
        data = {
            "model": model,
            "messages": [
                {
                    "role": "system",
                    "content": "You are a helpful assistant."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "max_tokens":max_tokens
        }
        response = requests.post("https://api.deepseek.com/chat/completions", headers=headers, json=data)
        #print(response.json())
        try:
            response_text = response.json()['choices'][0]['message']['content']
        except Exception as e:
            print(f"Error parsing initial queries: {e}")
            print(response.json())
            
        return self.remove_first_line(response_text.strip())