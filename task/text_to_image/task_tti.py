import asyncio
from datetime import datetime

from task._models.custom_content import Attachment
from task._utils.constants import API_KEY, DIAL_URL, DIAL_CHAT_COMPLETIONS_ENDPOINT
from task._utils.bucket_client import DialBucketClient
from task._utils.model_client import DialModelClient
from task._models.message import Message
from task._models.role import Role

class Size:
    """
    The size of the generated image.
    """
    square: str = '1024x1024'
    height_rectangle: str = '1024x1792'
    width_rectangle: str = '1792x1024'


class Style:
    """
    The style of the generated image. Must be one of vivid or natural.
     - Vivid causes the model to lean towards generating hyper-real and dramatic images.
     - Natural causes the model to produce more natural, less hyper-real looking images.
    """
    natural: str = "natural"
    vivid: str = "vivid"


class Quality:
    """
    The quality of the image that will be generated.
     - ‘hd’ creates images with finer details and greater consistency across the image.
    """
    standard: str = "standard"
    hd: str = "hd"

async def _save_images(attachments: list[Attachment]):
    #  1. Create DIAL bucket client
    async with DialBucketClient(base_url=DIAL_URL, api_key=API_KEY) as client:
        for attachment in attachments:
            if attachment.url and attachment.type == 'image/png':
                image_data = await client.get_file(attachment.url)
                filename = f"{datetime.now().strftime("%m-%d-%Y_%H%M%S")}.png"

                with open(filename, "wb") as file:
                    file.write(image_data)

                print(f"Saved image: {filename}")


        #  2. Iterate through Images from attachments, download them and then save here
        #  3. Print confirmation that image has been saved locally


def start() -> None:
    #  1. Create DialModelClient
    client = DialModelClient(endpoint=DIAL_CHAT_COMPLETIONS_ENDPOINT, deployment_name='dall-e-3', api_key=API_KEY)
    #  2. Generate image for "Sunny day on Bali"
    response = client.get_completion(messages=[Message(role=Role.USER,
                                                       content='Generate image for "Sunny day on Bali"')],
                                     custom_fields={
                                         "size": Size.square,
                                         "style": Style.vivid,
                                         "quality": Quality.hd,
                                     }
                                     )

    #  3. Get attachments from response and save generated message (use method `_save_images`)
    print(response)
    asyncio.run(_save_images(response.custom_content.attachments))

    #  4. Try to configure the picture for output via `custom_fields` parameter.
    #    - Documentation: See `custom_fields`. https://dialx.ai/dial_api#operation/sendChatCompletionRequest
    #  5. Test it with the 'imagegeneration@005' (Google image generation model)


start()
