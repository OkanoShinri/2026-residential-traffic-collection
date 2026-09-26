#!/usr/bin/env python3
"""このスクリプトが行うこと（これ以外の通信・ファイル操作は行わない）:
  - https://quic-resip.otsu36.netへGETリクエストを送る。h3とh2を交互に、それぞれ2000回（合計4000回）
  - 試行ごとに新しいセッションを作るため、毎回新しいハンドシェイクが発生する
  - 各試行の結果を attempts.log に、TLS の鍵を sslkeys.log に保存する（どちらも追記）

実行: uv run repeat.py
"""

import time
from datetime import datetime
from importlib.metadata import version
from pathlib import Path

import httpcloak

VERSIONS = ["h3", "h2"]

HERE = Path(__file__).resolve().parent
ATTEMPTS_LOG = HERE / "attempts.log"
KEYLOG = HERE / "sslkeys.log"

HEADERS = {"Accept-Language": "ja,en-US;q=0.9,en;q=0.8"}
SESSION_OPTIONS = {
    "preset": "chrome-latest",
    "timeout": 30,
    "quic_idle_timeout": 30,
    "retry": 0,
    "prefer_ipv4": True,
    "key_log_file": str(KEYLOG),
}

NOTICE = f"""\
このスクリプトは  https://quic-resip.otsu36.net へ HTTP/3とHTTP/2のリクエストを2000回ずつ、合計4000回送信します
（1秒間隔、所要時間の目安は 70〜120 分）。

以下の 2 ファイルがこのフォルダに保存され、提出していただきます:
  {ATTEMPTS_LOG.name} : 各試行の時刻・成否・所要時間
  {KEYLOG.name} : TLSの鍵(サーバー側で記録した通信の中身を復号できます)

また、サーバー側ではあなたのグローバルIPアドレスが記録されます。
"""


def record(f, message: str) -> None:
    line = f"{datetime.now().astimezone().isoformat(timespec='milliseconds')} {message}"
    print(line)
    f.write(line + "\n")
    f.flush()


def main() -> int:
    print(NOTICE)
    if input("内容に同意して開始する場合は yes と入力してください: ").strip().lower() != "yes":
        print("中止しました。")
        return 1

    ok = {v: 0 for v in VERSIONS}
    err = {v: 0 for v in VERSIONS}
    with ATTEMPTS_LOG.open("a", encoding="utf-8") as f:
        record(f, f'start url="https://quic-resip.otsu36.net" versions={",".join(VERSIONS)} n=2000 '
                  f"httpcloak={version('httpcloak')}")
        try:
            for i in range(1, 2001):
                for ver in VERSIONS:
                    started = time.monotonic()
                    try:
                        with httpcloak.Session(**SESSION_OPTIONS, http_version=ver) as s:
                            r = s.get("https://quic-resip.otsu36.net", headers=HEADERS)
                            result = f"ok  {r.protocol:<3} {r.status_code}"
                        ok[ver] += 1
                    except httpcloak.HTTPCloakError as e:
                        result = "err " + str(e).replace("\n", " ")
                        err[ver] += 1
                    record(f, f"#{i:04d} {ver} {result} {time.monotonic() - started:.2f}s")
                    time.sleep(1)
        except KeyboardInterrupt:
            record(f, "interrupted")
        record(f, "end " + " ".join(f"{v}:ok={ok[v]},err={err[v]}" for v in VERSIONS))

    print(f"\n完了しました。次の 2 ファイルを提出してください:\n  {ATTEMPTS_LOG}\n  {KEYLOG}")
    return 0 if any(ok.values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())
