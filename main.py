import asyncio
import uvloop

from Astandy import StandClient
from time import perf_counter
from Astandy.generated.listeners import (
    MarketplaceRemoteEventListenerOnTradeRequestOpenedUpdate,
    CreatePurchaseRequestBySaleRequest
)
from watched_items import WATCHED_ITEMS_1
asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
client = StandClient("d72ab43f1eed2e08ef99a2f0eaf6f961")

BUY_PRICES = {item_id: buy_price for item_id, (buy_price, _) in WATCHED_ITEMS_1.items()}
_make_req = client.raw.MarketplaceRemoteService.createPurchaseRequestBySale2Request
_send = client.send_request

async def buy_skin(sale_id: str):
    await _send(*_make_req(CreatePurchaseRequestBySaleRequest(saleId=sale_id)))

@client.MarketplaceRemoteEventListenerOnTradeRequestOpened()
async def trade_opened(client: StandClient, update: MarketplaceRemoteEventListenerOnTradeRequestOpenedUpdate):
    start_time = perf_counter()
    req = update.data.request
    if req.price <= BUY_PRICES[req.itemDefinitionId] and len(req.modifications) == 4:
        asyncio.create_task(buy_skin(req.id))
        end_time = perf_counter()
        print(f"[BUY ] Время выполнения с покупой: {(end_time - start_time) * 1000:.4f} мс")
        print(f"Успешно купил скин за {req.price}")

@client.OnConnect()
async def on_connect(client: StandClient, update):
    for item_id in WATCHED_ITEMS_1:
        await client.subscribe_trade(item_id)
        client.logger.info(f"Subscribed to item {item_id}")
    print("connected")

async def main():
    await client.start()
    await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(main())