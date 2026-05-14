import asyncio
import uvloop

from Astandy import StandClient
from time import perf_counter
from Astandy.generated.listeners import (
    MarketplaceRemoteEventListenerOnTradeRequestOpenedUpdate,
    CreatePurchaseRequestBySaleRequest
)
from watched_items import WATCHED_ITEMS_1

client = StandClient("051c0384c06cb8cf123ede0430c33c88")

BUY_PRICES = {item_id: buy_price for item_id, (buy_price, _) in WATCHED_ITEMS_1.items()}
_make_req = client.raw.MarketplaceRemoteService.createPurchaseRequestBySale2Request
_send = client.send_request

async def buy_skin(sale_id: str):
    await _send(*_make_req(CreatePurchaseRequestBySaleRequest(saleId=sale_id)))

@client.MarketplaceRemoteEventListenerOnTradeRequestOpened()
async def trade_opened(client: StandClient, update: MarketplaceRemoteEventListenerOnTradeRequestOpenedUpdate):
    req = update.data.request
    if req.price <= BUY_PRICES[req.itemDefinitionId] and len(req.modifications) == 4:
        await buy_skin(req.id)

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
    uvloop.install()
    asyncio.run(main())
