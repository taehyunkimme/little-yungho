"""
네이버 카페 글쓰기 독립 스크립트.
브라우저를 열고 글쓰기 페이지를 준비한 뒤, 사용자가 본문을 붙여넣고 등록하도록 한다.

사용법:
  python scripts/naver_cafe_writer.py \
    --title "포스팅 제목" \
    --content "채용 공고 본문" \
    --cookie-path data/naver_cookies.json \
    --prefix "긴급"
"""

import argparse
import json
import sys
import pyperclip
from playwright.sync_api import sync_playwright

CAFE_ID = "18633550"
WRITE_URL = f"https://cafe.naver.com/ca-fe/cafes/{CAFE_ID}/articles/write?boardType=L"


def main():
    parser = argparse.ArgumentParser(description="네이버 카페 글쓰기")
    parser.add_argument("--title", required=True, help="포스팅 제목")
    parser.add_argument("--content", required=True, help="포스팅 본문")
    parser.add_argument("--cookie-path", required=True, help="네이버 쿠키 파일 경로")
    parser.add_argument("--prefix", default="", help="말머리 (긴급, 진행중)")
    args = parser.parse_args()

    pw = sync_playwright().start()
    browser = pw.chromium.launch(headless=False)
    context = browser.new_context()

    with open(args.cookie_path, "r") as f:
        cookies = json.load(f)
    context.add_cookies(cookies)

    page = context.new_page()
    page.set_default_timeout(15000)

    # Step 1: 글쓰기 페이지로 이동
    page.goto(WRITE_URL)
    page.wait_for_load_state("domcontentloaded")
    page.wait_for_timeout(3000)

    title_field = page.locator("textarea.textarea_input")
    if not title_field.is_visible(timeout=5000):
        print(json.dumps({"status": "fail", "message": "글쓰기 페이지가 로드되지 않았습니다."}), flush=True)
        browser.close()
        pw.stop()
        sys.exit(1)

    # Step 2: 게시판 선택 (컨설팅/외국계)
    board_btn = page.locator('button:has-text("게시판을 선택해 주세요")').first
    if not board_btn.is_visible(timeout=3000):
        print(json.dumps({"status": "fail", "message": "게시판 선택 버튼을 찾을 수 없습니다."}), flush=True)
        browser.close()
        pw.stop()
        sys.exit(1)

    board_btn.click()
    page.wait_for_timeout(1000)

    page.evaluate('''() => {
        const container = document.querySelector('div.select_option.type_long');
        if (container) {
            container.scrollTop = container.scrollHeight;
        }
    }''')
    page.wait_for_timeout(500)

    board_option = page.locator('ul.option_list span.option_text').filter(has_text="컨설팅/외국계").first
    try:
        board_option.scroll_into_view_if_needed()
        page.wait_for_timeout(300)
        board_option.click()
    except Exception:
        clicked = page.evaluate('''() => {
            const spans = document.querySelectorAll('ul.option_list span.option_text');
            for (const span of spans) {
                if (span.textContent.trim() === '컨설팅/외국계') {
                    span.scrollIntoView({ block: 'center' });
                    span.click();
                    return true;
                }
            }
            return false;
        }''')
        if not clicked:
            print(json.dumps({"status": "fail", "message": "'컨설팅/외국계' 항목을 클릭할 수 없습니다."}), flush=True)
            browser.close()
            pw.stop()
            sys.exit(1)

    page.wait_for_timeout(500)

    still_unselected = page.locator('button:has-text("게시판을 선택해 주세요")').first
    try:
        if still_unselected.is_visible(timeout=1000):
            print(json.dumps({"status": "fail", "message": "게시판 선택이 반영되지 않았습니다."}), flush=True)
            browser.close()
            pw.stop()
            sys.exit(1)
    except Exception:
        pass

    # Step 3: 말머리 선택
    if args.prefix:
        try:
            prefix_btn = page.locator('button:has-text("말머리 선택")').first
            if prefix_btn.is_visible(timeout=2000):
                prefix_btn.click()
                page.wait_for_timeout(1000)
                page.locator(f"text={args.prefix}").last.click()
                page.wait_for_timeout(500)
        except Exception:
            pass

    # Step 4: 제목 입력
    title_field.click()
    page.wait_for_timeout(200)
    title_field.fill(args.title)
    page.wait_for_timeout(300)

    # Step 5: 채용 공고를 클립보드에 복사
    pyperclip.copy(args.content)

    print(json.dumps({"status": "success", "message": "글쓰기 준비 완료! 채용 공고가 클립보드에 복사되었습니다. 본문에 Cmd+V로 붙여넣고 등록하세요."}), flush=True)

    # 브라우저가 닫힐 때까지 대기 (사용자가 직접 닫음)
    try:
        page.wait_for_event("close", timeout=0)
    except Exception:
        pass

    try:
        browser.close()
    except Exception:
        pass
    try:
        pw.stop()
    except Exception:
        pass


if __name__ == "__main__":
    main()
