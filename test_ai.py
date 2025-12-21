import os
from volcenginesdkarkruntime import Ark 
from volcenginesdkarkruntime.types.images.images import SequentialImageGenerationOptions

client = Ark(
    base_url="https://ark.cn-beijing.volces.com/api/v3", 
    api_key=os.getenv('ARK_DOUBAO_SEEDREAM_API_KEY'), 
)

stream = client.images.generate(
    # Replace with Model ID
    model="doubao-seedream-4-5-251128",
    prompt="生成一组共4张连贯插画，核心为同一庭院一角的四季变迁，以统一风格展现四季独特色彩、元素与氛围",
    size="2000x2000",
    image=[],
    response_format="url",
    sequential_image_generation="auto",
    sequential_image_generation_options=SequentialImageGenerationOptions(max_images=3),
    watermark=False,
    stream=True,
)
for event in stream:
    if event is None:
        continue
    if event.type == "image_generation.partial_failed":
        print(f"Stream generate images error: {event.error}")
        if event.error is not None and event.error.code.equal("InternalServiceError"):
            break
    elif event.type == "image_generation.partial_succeeded":
        if event.error is None and event.url:
            print(f"recv.Size: {event.size}, recv.Url: {event.url}")
    elif event.type == "image_generation.completed":
        if event.error is None:
            print("Final completed event:")
            print("recv.Usage:", event.usage)
