"""WebSocket endpoints for real-time data streaming"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import Dict, Set, List
from datetime import datetime
import json
import asyncio
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

# Store active WebSocket connections
class ConnectionManager:
    def __init__(self):
        # active_connections: {symbol: set of websockets}
        self.active_connections: Dict[str, Set[WebSocket]] = {}
        # symbol_connections: {websocket: set of symbols}
        self.symbol_connections: Dict[WebSocket, Set[str]] = {}
        # watchlist_connections: {websocket: set of symbols (for watchlist updates)}
        self.watchlist_connections: Dict[WebSocket, Set[str]] = {}

    async def connect(self, websocket: WebSocket, symbol: str):
        """Connect a websocket to a symbol"""
        await websocket.accept()

        if symbol not in self.active_connections:
            self.active_connections[symbol] = set()
        self.active_connections[symbol].add(websocket)

        if websocket not in self.symbol_connections:
            self.symbol_connections[websocket] = set()
        self.symbol_connections[websocket].add(symbol)

        logger.info(f"WebSocket connected for symbol: {symbol}")

    async def connect_watchlist(self, websocket: WebSocket, symbols: List[str]):
        """Connect a websocket to multiple symbols for watchlist updates"""
        await websocket.accept()

        if websocket not in self.watchlist_connections:
            self.watchlist_connections[websocket] = set()

        for symbol in symbols:
            self.watchlist_connections[websocket].add(symbol)
            if symbol not in self.active_connections:
                self.active_connections[symbol] = set()
            self.active_connections[symbol].add(websocket)

        logger.info(f"WebSocket connected for watchlist: {symbols}")

    def disconnect(self, websocket: WebSocket):
        """Disconnect a websocket from all symbols"""
        if websocket in self.symbol_connections:
            for symbol in self.symbol_connections[websocket]:
                if symbol in self.active_connections:
                    self.active_connections[symbol].discard(websocket)
                    if not self.active_connections[symbol]:
                        del self.active_connections[symbol]
            del self.symbol_connections[websocket]

        if websocket in self.watchlist_connections:
            for symbol in self.watchlist_connections[websocket]:
                if symbol in self.active_connections:
                    self.active_connections[symbol].discard(websocket)
                    if not self.active_connections[symbol]:
                        del self.active_connections[symbol]
            del self.watchlist_connections[websocket]

        logger.info("WebSocket disconnected")

    async def broadcast_to_symbol(self, symbol: str, message: dict):
        """Broadcast a message to all websockets subscribed to a symbol"""
        if symbol in self.active_connections:
            disconnected = set()
            for connection in self.active_connections[symbol]:
                try:
                    await connection.send_json(message)
                except Exception as e:
                    logger.error(f"Error sending to websocket: {e}")
                    disconnected.add(connection)

            # Clean up disconnected websockets
            for conn in disconnected:
                self.disconnect(conn)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        """Send a message to a specific websocket"""
        try:
            await websocket.send_text(message)
        except Exception as e:
            logger.error(f"Error sending personal message: {e}")

manager = ConnectionManager()


@router.websocket("/ws/price/{symbol}")
async def websocket_price_endpoint(websocket: WebSocket, symbol: str):
    """
    WebSocket endpoint for real-time price updates for a single symbol

    Connect to: ws://localhost:8000/api/v2/assets/ws/price/{symbol}

    Example message format:
    {
        "type": "price_update",
        "symbol": "BTC-USD",
        "current_price": 65000.50,
        "bid": 64999.00,
        "ask": 65002.00,
        "change_24h": 1000.50,
        "change_percent_24h": 1.56,
        "timestamp": "2026-10-14T09:17:15Z"
    }
    """
    await manager.connect(websocket, symbol)

    try:
        # Send initial price data
        from ..core import data
        try:
            price_data = data.get_live_price(symbol)
            if price_data:
                initial_message = {
                    "type": "price_update",
                    "symbol": symbol,
                    "current_price": price_data.get("current_price"),
                    "bid": price_data.get("current_price", 0) * 0.999,  # Simulated bid
                    "ask": price_data.get("current_price", 0) * 1.001,  # Simulated ask
                    "change_24h": price_data.get("change_24h", 0),
                    "change_percent_24h": price_data.get("change_percent_24h", 0),
                    "timestamp": datetime.utcnow().isoformat() + "Z"
                }
                await websocket.send_json(initial_message)
        except Exception as e:
            logger.error(f"Error fetching initial price: {e}")

        # Keep connection alive and send periodic updates
        while True:
            try:
                # Simulate price updates every 5 seconds
                # In production, this would connect to a real data feed
                await asyncio.sleep(5)

                # Fetch current price
                price_data = data.get_live_price(symbol)
                if price_data:
                    update_message = {
                        "type": "price_update",
                        "symbol": symbol,
                        "current_price": price_data.get("current_price"),
                        "bid": price_data.get("current_price", 0) * 0.999,
                        "ask": price_data.get("current_price", 0) * 1.001,
                        "change_24h": price_data.get("change_24h", 0),
                        "change_percent_24h": price_data.get("change_percent_24h", 0),
                        "timestamp": datetime.utcnow().isoformat() + "Z"
                    }
                    await websocket.send_json(update_message)

                # Send ping to keep connection alive
                await websocket.send_json({"type": "ping", "timestamp": datetime.utcnow().isoformat() + "Z"})

            except WebSocketDisconnect:
                break
            except Exception as e:
                logger.error(f"Error in price update loop: {e}")
                # Send error message to client
                try:
                    await websocket.send_json({
                        "type": "error",
                        "message": str(e),
                        "timestamp": datetime.utcnow().isoformat() + "Z"
                    })
                except:
                    break
                await asyncio.sleep(1)  # Wait before retry

    except WebSocketDisconnect:
        manager.disconnect(websocket)
        logger.info(f"WebSocket disconnected for symbol: {symbol}")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        manager.disconnect(websocket)


@router.websocket("/ws/watchlist")
async def websocket_watchlist_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for real-time watchlist updates

    Connect to: ws://localhost:8000/api/v2/assets/ws/watchlist

    Client should send initial message with symbols:
    {
        "action": "subscribe",
        "symbols": ["AAPL", "BTC-USD", "MSFT"]
    }

    Server sends updates for all subscribed symbols:
    {
        "type": "watchlist_update",
        "updates": [
            {
                "symbol": "AAPL",
                "current_price": 185.50,
                "change_24h": 1.25,
                "change_percent_24h": 0.68,
                "timestamp": "2026-10-14T09:17:15Z"
            }
        ]
    }
    """
    await websocket.accept()

    subscribed_symbols = set()

    try:
        # Wait for initial subscription message
        init_message = await websocket.receive_json()

        if init_message.get("action") == "subscribe" and "symbols" in init_message:
            symbols = init_message["symbols"]
            if isinstance(symbols, list):
                subscribed_symbols = set(symbols)
                await manager.connect_watchlist(websocket, symbols)
                logger.info(f"Watchlist WebSocket subscribed to: {symbols}")

                # Send initial data for all symbols
                from ..core import data
                initial_updates = []
                for symbol in symbols:
                    try:
                        price_data = data.get_live_price(symbol)
                        if price_data:
                            initial_updates.append({
                                "symbol": symbol,
                                "current_price": price_data.get("current_price"),
                                "change_24h": price_data.get("change_24h", 0),
                                "change_percent_24h": price_data.get("change_percent_24h", 0),
                                "volume_24h": price_data.get("volume_24h", 0),
                                "high_24h": price_data.get("high_24h", 0),
                                "low_24h": price_data.get("low_24h", 0),
                                "timestamp": datetime.utcnow().isoformat() + "Z"
                            })
                    except Exception as e:
                        logger.error(f"Error fetching initial price for {symbol}: {e}")

                await websocket.send_json({
                    "type": "watchlist_update",
                    "updates": initial_updates
                })

        # Keep connection alive and send periodic updates
        while True:
            try:
                # Update every 5 seconds
                await asyncio.sleep(5)

                # Check for client messages (subscribe/unsubscribe)
                try:
                    message = await asyncio.wait_for(websocket.receive_json(), timeout=0.1)
                    if message.get("action") == "subscribe":
                        new_symbols = message.get("symbols", [])
                        if isinstance(new_symbols, list):
                            subscribed_symbols.update(new_symbols)
                            await manager.connect_watchlist(websocket, new_symbols)
                            logger.info(f"Added symbols to watchlist: {new_symbols}")
                    elif message.get("action") == "unsubscribe":
                        remove_symbols = message.get("symbols", [])
                        if isinstance(remove_symbols, list):
                            subscribed_symbols.difference_update(remove_symbols)
                            logger.info(f"Removed symbols from watchlist: {remove_symbols}")
                except asyncio.TimeoutError:
                    pass  # No message, continue with updates

                # Fetch and send updates for all subscribed symbols
                from ..core import data
                updates = []
                for symbol in subscribed_symbols:
                    try:
                        price_data = data.get_live_price(symbol)
                        if price_data:
                            updates.append({
                                "symbol": symbol,
                                "current_price": price_data.get("current_price"),
                                "change_24h": price_data.get("change_24h", 0),
                                "change_percent_24h": price_data.get("change_percent_24h", 0),
                                "volume_24h": price_data.get("volume_24h", 0),
                                "high_24h": price_data.get("high_24h", 0),
                                "low_24h": price_data.get("low_24h", 0),
                                "timestamp": datetime.utcnow().isoformat() + "Z"
                            })
                    except Exception as e:
                        logger.error(f"Error fetching price for {symbol}: {e}")

                if updates:
                    await websocket.send_json({
                        "type": "watchlist_update",
                        "updates": updates
                    })

                # Send ping to keep connection alive
                await websocket.send_json({"type": "ping", "timestamp": datetime.utcnow().isoformat() + "Z"})

            except WebSocketDisconnect:
                break
            except Exception as e:
                logger.error(f"Error in watchlist update loop: {e}")
                try:
                    await websocket.send_json({
                        "type": "error",
                        "message": str(e),
                        "timestamp": datetime.utcnow().isoformat() + "Z"
                    })
                except:
                    break
                await asyncio.sleep(1)

    except WebSocketDisconnect:
        manager.disconnect(websocket)
        logger.info("Watchlist WebSocket disconnected")
    except Exception as e:
        logger.error(f"Watchlist WebSocket error: {e}")
        manager.disconnect(websocket)
