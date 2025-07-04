import curses
import time
import random


def game_loop(stdscr):
    # 화면 초기 설정
    curses.curs_set(0)
    stdscr.nodelay(True)
    stdscr.timeout(50)

    max_y, max_x = stdscr.getmaxyx()

    # 플레이어의 초기 위치
    player_x = max_x // 2
    player_y = max_y - 1

    drops = []
    score = 0
    is_over = False

    while not is_over:
        try:
            # 터미널 크기 변화 감지
            new_max_y, new_max_x = stdscr.getmaxyx()
            if new_max_y != max_y or new_max_x != max_x:
                max_y, max_x = new_max_y, new_max_x
                player_y = max_y - 1
                player_x = min(player_x, max_x - 1)

            # 1) 입력처리
            key = stdscr.getch()
            if key == curses.KEY_LEFT:
                player_x = max(0, player_x - 1)
            elif key == curses.KEY_RIGHT:
                player_x = min(max_x - 1, player_x + 1)
            elif key == ord('q'):
                break

            # 2) 장애물 생성
            if random.random() < 0.1:
                drops.append([random.randint(0, max_x - 1), 0])

            # 3) 장애물 이동 & 충돌 검사
            new_drops = []
            for x, y in drops:
                if y + 1 == player_y and x == player_x:
                    is_over = True
                if y + 1 < max_y:
                    new_drops.append([x, y + 1])
                else:
                    score += 1
            drops = new_drops

            # 4) 화면 그리기 (예외 처리 추가)
            stdscr.clear()
            if max_y > 0 and max_x > 0:
                stdscr.addstr(0, 0, f"Score: {score}")
                if player_y < max_y and player_x < max_x:
                    stdscr.addstr(player_y, player_x, '𖨆')
                for x, y in drops:
                    if 0 <= y < max_y and 0 <= x < max_x:
                        stdscr.addstr(y, x, '|')
            stdscr.refresh()

            # 5) 프레임 속도 제어
            time.sleep(0.05)

        except curses.error:
            # 터미널 크기 변화나 기타 curses 오류 발생 시 무시하고 계속
            continue

    # Game Over 화면 처리
    show_game_over(stdscr, score)


def show_game_over(stdscr, score):
    """게임 오버 화면을 보여주고 키 입력을 기다리는 함수"""
    try:
        # 블로킹 모드로 전환
        stdscr.nodelay(False)
        stdscr.timeout(-1)  # 무한 대기

        # 입력 버퍼 완전히 비우기
        curses.flushinp()

        max_y, max_x = stdscr.getmaxyx()

        # 여러 번 입력 버퍼 비우기 (확실히 하기 위해)
        for _ in range(3):
            curses.flushinp()
            time.sleep(0.1)

        # 게임 오버 메시지 표시
        stdscr.clear()

        msg = "GAME OVER"
        score_msg = f"Final Score: {score}"
        continue_msg = "Press any key to exit..."

        # 메시지들을 화면 중앙에 배치
        if max_y > 4 and max_x > len(msg):
            stdscr.addstr(max_y // 2 - 1, (max_x - len(msg)) // 2, msg)
            stdscr.addstr(max_y // 2, (max_x - len(score_msg)) // 2, score_msg)
            stdscr.addstr(max_y // 2 + 2, (max_x - len(continue_msg)) // 2, continue_msg)
        else:
            # 터미널이 너무 작으면 간단히 표시
            stdscr.addstr(0, 0, f"GAME OVER - Score: {score}")
            stdscr.addstr(1, 0, "Press any key...")

        stdscr.refresh()

        # 확실한 키 입력 대기
        while True:
            try:
                key = stdscr.getch()
                if key != -1:  # 실제 키가 입력되었을 때만 종료
                    break
            except curses.error:
                continue
            time.sleep(0.05)  # CPU 사용량 줄이기

    except curses.error:
        # 화면 표시 오류 시 간단한 대기
        time.sleep(3)


if __name__ == '__main__':
    try:
        curses.wrapper(game_loop)
    except KeyboardInterrupt:
        print("게임이 중단되었습니다.")
    except Exception as e:
        print(f"게임 실행 중 오류 발생: {e}")