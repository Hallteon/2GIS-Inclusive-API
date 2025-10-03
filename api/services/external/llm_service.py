import aiohttp
from typing import Optional


class LLMService:
    def __init__(self, openrouter_api_key: str):
        self.api_key = openrouter_api_key
        self.base_url = "https://openrouter.ai/api/v1/chat/completions"
        self.model = "meta-llama/llama-4-maverick:free"

    async def send_query(self, system_prompt: str, user_content: str, image_base64: str = None) -> str:
        """
        Создает тифлокомментарий для изображения.

        Args:
            system_prompt (str): системный промпт.
            user_content (str): текстовый запрос пользователя.
            image_base64 (str, optional): изображение в формате base64. По умолчанию None.

        Returns:
            str: ответ от модели.
        """

        messages = [{"role": "system", "content": system_prompt}]

        user_message_content = [{"type": "text", "text": user_content}]

        if image_base64:
            image_data_url = f"data:image/jpeg;base64,{image_base64}"
            user_message_content.append({
                "type": "image_url",
                "image_url": {
                    "url": image_data_url
                }
            })

        messages.append({
            "role": "user",
            "content": user_message_content
        })

        payload = {
            "model": self.model,
            "messages": messages,
            "max_tokens": 800,
            "temperature": 0.6,
            "top_p": 0.9
        }

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/Hallteon/Shedevro.Sber-API",
            "X-Title": "BlindLLMService"
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(self.base_url, json=payload, headers=headers) as response:
                    if response.status == 200:
                        result = await response.json()
                        return result["choices"][0]["message"]["content"]
                    else:
                        error_text = await response.text()
                        raise Exception(f"OpenRouter API error: {response.status} - {error_text}")
        except Exception as e:
            return f"Ошибка при отправке запроса: {str(e)}"