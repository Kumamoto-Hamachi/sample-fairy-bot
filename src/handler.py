import logging
import os
from datetime import datetime
from zoneinfo import ZoneInfo

from slack_bolt import App
from slack_bolt.adapter.aws_lambda import SlackRequestHandler
from slack_sdk.web import WebClient

# from ./constants import ZUNDA_EMOJI
ZUNDA_EMOJI = "zundamon"

app = App(
    token=os.environ.get("SLACK_BOT_TOKEN"),
    signing_secret=os.environ.get("SLACK_SIGNING_SECRET"),
    # process_before_response=True
)
bot_user = os.environ.get("SLACK_BOT_USER")
register = App(
    token=os.environ.get("SLACK_USER_TOKEN"),
    # process_before_response=True
)

logger = logging.getLogger()
logger.setLevel(logging.INFO)


@app.event("reaction_added")
def reply_nanoda(client: WebClient, event: dict) -> None:
    """
    特定の絵文字(ZUNDA_EMOJI)が押された際に
    ボットから定型文メッセージをスレッドに返信
    """
    logger.info("reply_nanoda start")  # debug
    reaction: str = event["reaction"]
    logger.info("reaction", reaction)  # debug
    mes = _greeting()
    if reaction == ZUNDA_EMOJI:
        logger.info("ZUNDA EMOJI reaction")  # debug
        client.chat_postMessage(
            channel=event["item"]["channel"],
            thread_ts=event["item"]["ts"],
            text=mes,
        )
    logger.info("reply_nanoda end")  # debug


def _greeting() -> str:
    """
    時間に応じてずんだもんの挨拶の冒頭を変える
    """
    now = datetime.now(ZoneInfo("Asia/Tokyo"))
    logger.info("now", now)  # debug
    now_hour: int = now.hour
    prefix = ""
    if 6 <= now_hour <= 10:
        prefix = "おはようございます。\n"
    elif 11 <= now_hour <= 16:
        prefix = "こんにちは。\n"
    elif 17 <= now_hour <= 24:
        prefix = "こんばんは。\n"
    else:
        prefix = "くそねみぃのだ...\n"
    return prefix + "僕、ずんだもんなのだ。"


@app.event("channel_created")
def register_nanoda(event: dict) -> None:
    """
    新しいチャンネルが作成されるたびに、
    ずんだもんbotを該当のチャンネルに登録(招待)
    """
    logger.info("register_nanoda start")  # debug
    channel = event.get("channel", dict())
    channel_id = channel.get("id")
    if channel_id and bot_user:
        res = register.client.conversations_invite(
            channel=channel_id,
            users=bot_user,
        )
        logger.info("res", res)  # debug
    logger.info("register_nanoda end")  # debug


def handler(event, context):
    slack_handler = SlackRequestHandler(app=app)
    return slack_handler.handle(event, context)
