import asyncio
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from src.core.assistant import SERA
from src.voice.stt import speech_to_text
from src.voice.tts import text_to_speech

router = APIRouter()
sera = SERA()


@router.websocket("/ws/chat")
async def websocket_chat(websocket: WebSocket):
    await websocket.accept()

    try:
        while True:
            try:
                data = await websocket.receive_json()
            except Exception:
                await websocket.send_json(
                    {"type": "error", "message": "Invalid message format"}
                )
                continue

            msg_type = data.get("type")
            session_id = data.get("session_id")
            user_id = data.get("user_id")

            if not all([msg_type, session_id, user_id]):
                await websocket.send_json(
                    {"type": "error", "message": "Missing required fields"}
                )
                continue

            # 🎙️ AUDIO INPUT
            if msg_type == "audio":
                message = await asyncio.to_thread(speech_to_text, data.get("data"))

                if not message:
                    continue

                await websocket.send_json({"type": "transcript", "data": message})

            # ⌨️ TEXT INPUT
            elif msg_type == "text":
                message = data.get("data", "").strip()
                if not message:
                    continue
            else:
                await websocket.send_json(
                    {"type": "error", "message": "Unknown message type"}
                )
                continue

            # 🧠 STREAM RESPONSE
            buffer = ""

            try:
                async for token in sera.respond_stream(
                    message=message, session_id=session_id, user_id=user_id
                ):
                    buffer += token

                    # Flush buffer every ~40 chars
                    if len(buffer) >= 40:
                        audio_chunk = await asyncio.to_thread(text_to_speech, buffer)
                        buffer = ""

                        await websocket.send_json(
                            {"type": "audio_chunk", "data": audio_chunk}
                        )

                # Flush remaining buffer
                if buffer:
                    audio_chunk = await asyncio.to_thread(text_to_speech, buffer)
                    await websocket.send_json(
                        {"type": "audio_chunk", "data": audio_chunk}
                    )

                await websocket.send_json({"type": "end"})

            except WebSocketDisconnect:
                print("Client disconnected during streaming")
                break

    except WebSocketDisconnect:
        print("Voice WebSocket disconnected")
