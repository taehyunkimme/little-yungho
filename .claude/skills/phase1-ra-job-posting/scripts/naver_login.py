"""
네이버 로그인 세션 저장 스크립트.
브라우저를 열고 사용자가 수동 로그인하면 쿠키를 저장한다.

사용법: python scripts/naver_login.py --cookie-path data/naver_cookies.json
"""

import argparse
import json
import os
import sys
from playwright.sync_api import sync_playwright


def main():
    parser = argparse.ArgumentParser(description="네이버 로그인 세션 저장")
    parser.add_argument("--cookie-path", required=True, help="쿠키 저장 경로")
    args = parser.parse_args()

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False)
            context = browser.new_context()
            page = context.new_page()
            page.goto("https://nid.naver.com/nidlogin.login")

            print("네이버 로그인 페이지가 열렸습니다. 로그인을 완료해주세요... (120초 타임아웃)", flush=True)
            page.wait_for_url("https://www.naver.com/**", timeout=120000)

            cookies = context.cookies()
            os.makedirs(os.path.dirname(args.cookie_path), exist_ok=True)
            with open(args.cookie_path, "w") as f:
                json.dump(cookies, f)

            browser.close()
            print(json.dumps({"status": "success", "message": "네이버 로그인 세션이 저장되었습니다."}), flush=True)
    except Exception as e:
        print(json.dumps({"status": "fail", "message": f"로그인 실패: {str(e)}"}), flush=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
