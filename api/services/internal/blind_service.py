from fastapi.params import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from api.database import get_async_session

from api.utils.llm_promts import image_describe_promt, user_request_template
from api.services.external.llm_service import LLMService

from settings import config_parameters


class BlindHelpService:
    def __init__(self, session: AsyncSession = Depends(get_async_session)):
        self.session = session

    async def create_description(self, image: str, description: str = None) -> str:
        system_prompt = image_describe_promt
        user_content = user_request_template.format(image_length=len(image),
                                                    additional_info=f"ДОПОЛНИТЕЛЬНАЯ ИНФОРМАЦИЯ ОТ ПОЛЬЗОВАТЕЛЯ: "
                                                                    f"{description}" if description else "Дополнительной информации от пользователя нет.")

        llm_response = await LLMService(
            openrouter_api_key=config_parameters.OPENROUTER_API_KEY
        ).send_query(
            system_prompt=system_prompt,
            user_content=user_content,
            image_base64=image
        )

        return llm_response