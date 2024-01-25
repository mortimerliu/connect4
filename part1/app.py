#!/usr/bin/env python

import json
import itertools
import asyncio
import websockets

from connect4 import PLAYER1, PLAYER2, Connect4


async def handler(websocket):
    game = Connect4()

    turns = itertools.cycle([PLAYER1, PLAYER2])
    player = next(turns)

    async for message in websocket:
        event = json.loads(message)
        assert event["type"] == "play"
        column = event["column"]

        try:
            row = game.play(player, column)
        except RuntimeError as e:
            await websocket.send(
                json.dumps({"type": "error", "message": str(e)})
            )
        else:
            await websocket.send(
                json.dumps(
                    {
                        "type": "play",
                        "player": game.last_player,
                        "column": column,
                        "row": row,
                    }
                )
            )
            if game.winner is not None:
                await websocket.send(
                    json.dumps({"type": "win", "player": game.winner})
                )

            player = next(turns)


async def main():
    async with websockets.serve(handler, "", 8001):
        await asyncio.Future()  # run forever


if __name__ == "__main__":
    asyncio.run(main())
