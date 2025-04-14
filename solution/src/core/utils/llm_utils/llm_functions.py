import json

from yandex_cloud_ml_sdk import YCloudML

from src.core.data import settings
from src.core.utils.llm_utils import schemas as llm_schemas

sdk = YCloudML(
    auth=settings.yandex_api_key,
    folder_id=settings.yandex_folder_id,
)


async def moderate_text_with_llm(
    ad_text: str,
    ad_title: str,
) -> llm_schemas.LLMModerateResponse:
    messages = [
        {
            "role": "system",
            "text": (
                "Ты — помощник, который проверяет рекламный текст и заголовок на наличие нежелательного "
                "контента. Нежелательный контент включает матерные слова, оскорбления, дискриминацию, "
                "ненормативную лексику и другие недопустимые выражения. Без форматирования, без Markdown"
                "Верни ответ ТОЛЬКО в JSON-формате с полями 'status' (boolean) и 'reason' (string или null). "
                "Никаких дополнительных объяснений или текста - только валидный JSON!"
            ),
        },
        {
            "role": "user",
            "text": (
                f"Проверь следующий рекламный текст и заголовок: \n"
                f"Текст: '{ad_text}'\n"
                f"Заголовок: '{ad_title}'\n"
                f"Если найдены проблемы, укажи их в поле 'reason'. Если все в порядке, "
                f"верни 'status': true и 'reason': null."
            ),
        },
    ]

    try:
        response = (
            sdk.models.completions(f"yandexgpt")
            .configure(temperature=0.5)
            .run(messages)
        )
        content = (
            response.alternatives[0]
            .text.replace("```", "")
            .replace("\n", "")
            .replace("```json", "")
            .strip()
        )
    except Exception as e:
        raise ValueError("Ошибка при генерации рекламного поста: " + str(e))
    response_json = json.loads(content)
    return llm_schemas.LLMModerateResponse.model_validate(response_json)


async def generate_ad_post(description: str) -> llm_schemas.LLMGeneratedAd:
    messages = [
        {
            "role": "system",
            "text": (
                "Ты — эксперт по созданию рекламных постов. Твоя задача — сгенерировать привлекательный "
                "заголовок и текст на основе предоставленного описания. "
                "Верни ответ ТОЛЬКО в JSON-формате с полями 'ad_title' (string) и 'ad_text' (string). "
                "Никакого форматирования, без Markdown, только чистый JSON! Убедись, что текст соответствует"
                " этическим стандартам и не содержит нежелательного контента."
            ),
        },
        {
            "role": "user",
            "text": (
                f"Создай рекламный пост на основе следующего описания: \n"
                f"'{description}'\n"
                f"Заголовок должен быть кратким и привлекательным, а текст — информативным и убедительным."
            ),
        },
    ]
    try:
        response = (
            sdk.models.completions(f"yandexgpt")
            .configure(temperature=0.5)
            .run(messages)
        )
        content = (
            response.alternatives[0]
            .text.replace("```", "")
            .replace("\n", "")
            .replace("```json", "")
            .strip()
        )
    except Exception as e:
        raise ValueError("Ошибка при генерации рекламного поста: " + str(e))

    response_json = json.loads(content)
    return llm_schemas.LLMGeneratedAd.model_validate(response_json)
