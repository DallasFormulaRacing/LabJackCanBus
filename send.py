import asyncio
import traceback
import os
from dotenv import load_dotenv

from azure.eventhub import EventData
from azure.eventhub.aio import EventHubProducerClient

load_dotenv()

EVENT_HUB_CONNECTION_STR = os.getenv('EVENT_HUB_CONNECTION_STR')
EVENT_HUB_NAME = os.getenv('EVENT_HUB_NAME')


async def run():
    # Create a producer client to send messages to the event hub.
    # Specify a connection string to your event hubs namespace and
    # the event hub name.
    try:

      producer = EventHubProducerClient.from_connection_string(
          conn_str=EVENT_HUB_CONNECTION_STR, eventhub_name=EVENT_HUB_NAME
      )
      async with producer:
          # Create a batch.
          event_data_batch = await producer.create_batch()

          # Add events to the batch.
          event_data_batch.add(EventData("First event "))
          event_data_batch.add(EventData("Second event"))
          event_data_batch.add(EventData("Third event"))

          # Send the batch of events to the event hub.
          await producer.send_batch(event_data_batch)

          print("Batch of events sent")

    except Exception as e:
        print(e + traceback.format_exc())

asyncio.run(run())  
