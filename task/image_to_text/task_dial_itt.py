import asyncio
from io import BytesIO
from pathlib import Path

from task._models import custom_content
from task._models.custom_content import Attachment, CustomContent
from task._utils.constants import API_KEY, DIAL_URL, DIAL_CHAT_COMPLETIONS_ENDPOINT
from task._utils.bucket_client import DialBucketClient
from task._utils.model_client import DialModelClient
from task._models.message import Message
from task._models.role import Role


async def _put_image(file_name : str, mime_type) -> Attachment:
    image_path = Path(__file__).parent.parent.parent / file_name

    #  1. Create DialBucketClient
    async with DialBucketClient(api_key=API_KEY, base_url=DIAL_URL) as bucket_client:

        #  2. Open image file
        with open(image_path, 'rb') as image_file:
            file_bytes = image_file.read()

        #  3. Use BytesIO to load bytes of image
        image_content = BytesIO(file_bytes)

        #  4. Upload file with client
        attachment = await bucket_client.put_file(name=file_name,
                                                     mime_type=mime_type,
                                                     content = image_content)

        #  5. Return Attachment object with title (file name), url and type (mime type)
        return Attachment(title=file_name,
                          url=attachment.get("url"),
                          type=mime_type)

def start() -> None:

    #  2. Upload image (use `_put_image` method )
    attachment1 = asyncio.run(_put_image('dialx-banner.png', 'image/png'))
    attachment2 = asyncio.run(_put_image('pic2.jpg', 'image/jpg'))

    #  3. Print attachment to see result
    print(f"Attachment 1: {attachment1}")
    print(f"Attachment 2: {attachment2}")

    deployment_names = ['gpt-4o', 'gemini-2.5-pro'] # FYI gemini throws error for jpeg as this file type is not supported
    for deployment_name in deployment_names:
        print(f"Deployment name: {deployment_name}")

        #  1. Create DialModelClient
        model_client = DialModelClient(endpoint=DIAL_CHAT_COMPLETIONS_ENDPOINT, api_key=API_KEY,
                                       deployment_name=deployment_name)

        #  4. Call chat completion via client with list containing one Message:
        #    - role: Role.USER
        #    - content: "What do you see on this picture?"
        #    - custom_content: CustomContent(attachments=[attachment])
        #  ---------------------------------------------------------------------------------------------------------------
        #  Note: This approach uploads the image to DIAL bucket and references it via attachment. The key benefit of this
        #        approach that we can use Models from different vendors (OpenAI, Google, Anthropic). The DIAL Core
        #        adapts this attachment to Message content in appropriate format for Model.

        model_client.get_completion(messages=[Message(role=Role.USER,
                                                      content="What do you see on this pictures?",
                                                      custom_content=CustomContent(attachments=[attachment1, attachment2]))])

        #  TRY THIS APPROACH WITH DIFFERENT MODELS!
        #  Optional: Try upload 2+ pictures for analysis


start()
