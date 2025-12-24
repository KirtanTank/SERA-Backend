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
            data = await websocket.receive_json()

            msg_type = data["type"]
            session_id = data["session_id"]
            user_id = data["user_id"]

            # 🎙️ AUDIO INPUT
            if msg_type == "audio":
                message = speech_to_text(data["data"])

                await websocket.send_json({
                    "type": "transcript",
                    "data": message
                })

            # ⌨️ TEXT INPUT
            else:
                message = data["data"]

            # 🧠 STREAM RESPONSE
            async for token in sera.respond_stream(
                message=message,
                session_id=session_id,
                user_id=user_id
            ):
                audio_chunk = text_to_speech(token)

                await websocket.send_json({
                    "type": "audio_chunk",
                    "data": audio_chunk
                })

            await websocket.send_json({"type": "end"})

    except WebSocketDisconnect:
        print("Voice WebSocket disconnected")
