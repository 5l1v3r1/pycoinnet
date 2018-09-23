import logging

from pycoinnet.aitertools import preload_aiter, aiter_to_iter

from pycoinnet.header_improvements import header_improvements_aiter

from .BlockBatcher import BlockBatcher


async def peer_lifecycle(remote_peer_aiter, rate_limiter):
    rate_limiter.push(1)
    async for peer in remote_peer_aiter:
        logging.info("connected to %s", peer)
        yield peer
        await peer.wait_until_close()
        logging.info("close connection to %s", peer)
        rate_limiter.push(1)


async def blockcatchup(peer_manager, blockchain_view, count=4):

    block_batcher = BlockBatcher(peer_manager)

    async for idx, f in preload_aiter(2500, block_batcher.block_futures_for_header_info_aiter(
            header_improvements_aiter(peer_manager, blockchain_view, block_batcher, count))):
        peer, block = await f
        yield peer, block, idx
    logging.info("caught up blocks, waiting for tasks")
    await peer_manager.close_all()
    await block_batcher.join()


def fetch_blocks_after(peer_manager, blockchain_view, peer_count, filter_f=None):
    for peer, block, index in aiter_to_iter(blockcatchup(peer_manager, blockchain_view, peer_count)):
        yield block, index
